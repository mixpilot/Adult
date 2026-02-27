from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from datetime import timedelta, datetime
import json
import logging
import random
import string

from decimal import Decimal

logger = logging.getLogger(__name__)
from .models import (
    SubscriptionPlan, Subscription, Payment, PromoCode,
    Token, TokenTransaction, CreatorEarning, PayPerViewPurchase, Tip
)
from .forms import SubscriptionForm, PromoCodeForm, TokenPurchaseForm, TipForm
from content.models import Content


def ensure_default_plans():
    """Create the three default plans (250/mo, 500/mo, 100 once) if not already present. Visible to both."""
    # Already have the default set (Standard, Premium, One Time for both)
    if SubscriptionPlan.objects.filter(tier__in=('basic', 'premium', 'once'), user_type='both', is_active=True).count() >= 3:
        return
    plans_data = [
        {'tier': 'basic', 'user_type': 'both', 'name': 'Standard', 'price_monthly': Decimal('250.00'),
         'description': 'Access verified escorts, message and connect. Perfect to get started.',
         'unlimited_messaging': True, 'unlimited_content_access': True, 'ad_free': False, 'advanced_search': True},
        {'tier': 'premium', 'user_type': 'both', 'name': 'Premium', 'price_monthly': Decimal('500.00'),
         'price_quarterly': Decimal('1350.00'), 'price_yearly': Decimal('4800.00'),
         'description': 'Full access, priority support, and ad-free experience. Best value.',
         'unlimited_messaging': True, 'unlimited_content_access': True, 'ad_free': True, 'advanced_search': True, 'priority_support': True},
        {'tier': 'once', 'user_type': 'both', 'name': 'One Time Access', 'price_monthly': Decimal('100.00'),
         'description': 'One-time payment for 30 days access. No renewal.',
         'unlimited_messaging': True, 'unlimited_content_access': True, 'ad_free': False, 'advanced_search': True},
    ]
    for d in plans_data:
        SubscriptionPlan.objects.get_or_create(
            tier=d['tier'], user_type=d['user_type'],
            defaults={k: v for k, v in d.items() if k not in ('tier', 'user_type')},
        )


@login_required
def subscription_plans(request):
    """Display subscription plans based on user type."""
    ensure_default_plans()
    user_type = request.user.user_type
    is_new_user = request.GET.get('new_user') == '1'
    
    plans = list(
        SubscriptionPlan.objects.filter(is_active=True)
        .filter(models.Q(user_type=user_type) | models.Q(user_type='both'))
        .order_by('price_monthly')
    )
    if not plans:
        plans = list(SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly'))
    
    # Also get plans for the other type (for switching)
    other_type = 'escort' if user_type == 'client' else 'client'
    other_plans = SubscriptionPlan.objects.filter(
        is_active=True,
        user_type=other_type
    ).order_by('price_monthly')
    
    # Check if user has active subscription
    current_subscription = None
    if hasattr(request.user, 'subscription'):
        current_subscription = request.user.subscription
    
    context = {
        'plans': plans,
        'other_plans': other_plans,
        'current_subscription': current_subscription,
        'user_type': user_type,
        'other_type': other_type,
        'is_new_user': is_new_user,
    }
    return render(request, 'subscriptions/plans.html', context)


def generate_transaction_reference():
    """Generate unique transaction reference."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@login_required
def review_subscription(request):
    """Review subscription plan details before payment."""
    plan_id = request.GET.get('plan')
    if not plan_id:
        messages.error(request, "Please select a plan first.")
        return redirect('subscriptions:plans')
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        messages.error(request, "Selected plan not found.")
        return redirect('subscriptions:plans')
    
    # Check if plan is for user's type
    user_type = request.user.user_type
    if plan.user_type not in [user_type, 'both']:
        messages.warning(request, "This plan is not available for your account type.")
        return redirect('subscriptions:plans')
    
    # Check ID verification requirement for Premium/VIP plans
    if plan.tier in ['premium', 'vip']:
        if not request.user.is_id_verified():
            messages.warning(
                request, 
                f'ID verification is required for {plan.name} plans. Please verify your ID before subscribing.'
            )
            return redirect('accounts:profile')
    
    # Handle form submission (billing period and promo code selection)
    if getattr(plan, 'is_one_time_plan', plan.tier == 'once'):
        billing_period = 'once'
    else:
        billing_period = request.GET.get('billing_period', 'monthly')
    promo_code_text = request.GET.get('promo_code', '').strip()
    
    # Calculate pricing
    base_price = plan.get_price(billing_period)
    promo_code = None
    discount_amount = 0
    final_price = base_price
    
    if promo_code_text:
        try:
            promo_code = PromoCode.objects.get(code__iexact=promo_code_text, is_active=True)
            is_valid, message = promo_code.is_valid(user=request.user, plan=plan)
            if is_valid:
                discount_amount = promo_code.calculate_discount(base_price)
                final_price = base_price - discount_amount
            else:
                messages.warning(request, f"Promo code invalid: {message}")
        except PromoCode.DoesNotExist:
            if promo_code_text:
                messages.warning(request, "Promo code not found.")
    
    # Calculate savings for different billing periods
    monthly_price = plan.price_monthly
    quarterly_price = plan.get_price('quarterly')
    yearly_price = plan.get_price('yearly')
    
    quarterly_savings = (monthly_price * 3) - quarterly_price if plan.price_quarterly else 0
    yearly_savings = (monthly_price * 12) - yearly_price if plan.price_yearly else 0
    
    context = {
        'plan': plan,
        'billing_period': billing_period,
        'base_price': base_price,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'promo_code': promo_code,
        'promo_code_text': promo_code_text,
        'monthly_price': monthly_price,
        'quarterly_price': quarterly_price,
        'yearly_price': yearly_price,
        'quarterly_savings': quarterly_savings,
        'yearly_savings': yearly_savings,
        'user_type': user_type,
        'is_one_time_plan': getattr(plan, 'is_one_time_plan', plan.tier == 'once'),
    }
    return render(request, 'subscriptions/review.html', context)


@login_required
def subscribe(request):
    """Handle subscription payment form submission."""
    logger.warning('[subscribe] ENTRY method=%s POST_keys=%s', request.method, list(request.POST.keys()))

    # Get plan, billing period, and promo code from POST or query params
    plan_id = request.POST.get('plan') or request.GET.get('plan')
    billing_period = request.POST.get('billing_period', 'monthly')
    promo_code_text = request.POST.get('promo_code', '').strip()
    logger.warning('[subscribe] plan_id=%s billing_period=%s promo_code_text=%r', plan_id, billing_period, promo_code_text)

    if not plan_id:
        logger.warning('[subscribe] REDIRECT → plans (no plan_id)')
        messages.error(request, "Please select a plan first.")
        return redirect('subscriptions:plans')

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        logger.warning('[subscribe] REDIRECT → plans (plan not found id=%s)', plan_id)
        messages.error(request, "Selected plan not found.")
        return redirect('subscriptions:plans')

    if request.method != 'POST':
        logger.warning('[subscribe] REDIRECT → review (method not POST)')
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    # POST: payment details
    payment_method = request.POST.get('payment_method')
    phone_number = request.POST.get('phone_number', '').strip()
    logger.warning('[subscribe] payment_method=%r phone_number=%r', payment_method, phone_number or '(empty)')

    if not payment_method:
        logger.warning('[subscribe] REDIRECT → review (missing payment_method)')
        messages.error(request, "Please select a payment method.")
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    if payment_method != 'paystack' and not phone_number:
        logger.warning('[subscribe] REDIRECT → review (missing phone_number for non-paystack method)')
        messages.error(request, "Please provide your phone number.")
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    # Validate promo code if provided
    promo_code = None
    discount_amount = 0
    if promo_code_text:
        try:
            promo_code = PromoCode.objects.get(code__iexact=promo_code_text, is_active=True)
            is_valid, message = promo_code.is_valid(user=request.user, plan=plan)
            if not is_valid:
                logger.warning('[subscribe] REDIRECT → review (invalid promo: %s)', message)
                messages.error(request, f"Invalid promo code: {message}")
                return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")
        except PromoCode.DoesNotExist:
            logger.warning('[subscribe] REDIRECT → review (promo not found)')
            messages.error(request, "Invalid promo code")
            return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    # Check ID verification requirement for Premium/VIP plans
    if plan.tier in ['premium', 'vip']:
        if not request.user.is_id_verified():
            logger.warning('[subscribe] REDIRECT → accounts:profile (ID verification required)')
            messages.warning(
                request,
                f'ID verification is required for {plan.name} plans. Please verify your ID before subscribing.'
            )
            return redirect('accounts:profile')

    # Calculate price
    price = plan.get_price(billing_period)
    if promo_code:
        discount_amount = promo_code.calculate_discount(price)
        final_price = price - discount_amount
    else:
        final_price = price
    logger.warning('[subscribe] final_price=%s plan.tier=%s', final_price, plan.tier)

    # Generate transaction reference and create pending payment
    transaction_ref = generate_transaction_reference()
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        amount=final_price,
        payment_method=payment_method,
        phone_number=phone_number,
        transaction_reference=transaction_ref,
        status='pending',
        billing_period=billing_period,
    )

    if phone_number:
        request.user.phone_number = phone_number
        request.user.save(update_fields=['phone_number'])

    if payment_method == 'paystack':
        from payments.services import PaystackService

        callback_path = reverse('payments:paystack_callback')
        callback_base_url = getattr(settings, 'PAYSTACK_CALLBACK_BASE_URL', '').rstrip('/')
        callback_url = f'{callback_base_url}{callback_path}' if callback_base_url else request.build_absolute_uri(callback_path)
        email = (request.user.email or f'user{request.user.id}@example.com').strip()
        metadata = {
            'payment_id': payment.id,
            'user_id': request.user.id,
            'plan_id': plan.id,
            'billing_period': billing_period,
        }

        logger.warning('[subscribe] Initializing Paystack payment_id=%s email=%s amount=%s', payment.id, email, final_price)
        result = PaystackService().initialize_transaction(
            email=email,
            amount=final_price,
            reference=transaction_ref,
            callback_url=callback_url,
            metadata=metadata,
            currency=payment.currency,
        )
        logger.warning('[subscribe] Paystack init result success=%s error=%s', result.get('success'), result.get('error_message', ''))

        if result.get('success'):
            return redirect(result.get('authorization_url'))

        payment.status = 'failed'
        payment.save(update_fields=['status', 'updated_at'])
        messages.error(request, result.get('error_message') or 'Could not initialize Paystack payment.')
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    # M-Pesa prompt (STK Push): trigger prompt and redirect to waiting page
    if payment_method != 'mpesa':
        logger.warning('[subscribe] REDIRECT → payment_instructions (payment_method=%s not mpesa)', payment_method)
        return redirect('subscriptions:payment_instructions', payment_id=payment.id)

    from payments.services import MpesaService
    from payments.models import MpesaTransaction

    logger.warning('[subscribe] Calling M-Pesa STK push payment_id=%s phone=%s amount=%s', payment.id, phone_number, final_price)
    account_ref = f'sub_{payment.id}'
    desc = f'{plan.name} {billing_period}'[:13]
    service = MpesaService()
    result = service.initiate_stk_push(
        phone_number=phone_number,
        amount=final_price,
        account_reference=account_ref,
        transaction_desc=desc,
    )
    logger.warning('[subscribe] STK result: success=%s error_message=%s', result.get('success'), result.get('error_message', ''))

    if result['success']:
        MpesaTransaction.objects.create(
            account_reference=account_ref,
            transaction_desc=desc,
            phone_number=service.normalize_phone(phone_number),
            amount=final_price,
            checkout_request_id=result['checkout_request_id'],
            merchant_request_id=result['merchant_request_id'],
            status='pending',
        )
        logger.warning('[subscribe] REDIRECT → mpesa_waiting payment_id=%s', payment.id)
        return redirect('subscriptions:mpesa_waiting', payment_id=payment.id)

    # STK failed: send back to review to try again.
    logger.warning('[subscribe] REDIRECT → review (STK failed: %s)', result.get('error_message', ''))
    messages.error(request, result.get('error_message', 'M-Pesa prompt could not be sent. Check your number and try again.'))
    return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")


@login_required
def subscription_success(request):
    """Handle successful subscription (after payment verification)."""
    payment_id = request.GET.get('payment_id')
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            if payment.status == 'completed':
                messages.success(request, "Subscription activated successfully!")
            else:
                messages.info(request, "Payment received! Your subscription will be activated shortly.")
        except Payment.DoesNotExist:
            messages.error(request, "Payment not found")
    
    return redirect('subscriptions:manage')


@login_required
def manage_subscription(request):
    """Manage user's subscription and payment history."""
    subscription = None
    if hasattr(request.user, 'subscription'):
        subscription = request.user.subscription

    payment_history = Payment.objects.filter(user=request.user).select_related('plan').order_by('-created_at')[:50]

    context = {
        'subscription': subscription,
        'payment_history': payment_history,
    }
    return render(request, 'subscriptions/manage.html', context)


@login_required
def mpesa_waiting(request, payment_id):
    """Shown after M-Pesa STK push was sent – user completes payment on phone."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    if payment.payment_method != 'mpesa':
        return redirect('subscriptions:payment_instructions', payment_id=payment_id)
    if payment.status == 'completed':
        messages.success(request, 'Payment completed. Your subscription is active.')
        return redirect('subscriptions:manage')
    context = {'payment': payment}
    return render(request, 'subscriptions/mpesa_waiting.html', context)


@login_required
def payment_instructions(request, payment_id):
    """Display mobile payment instructions."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Get payment instructions based on method
    payment_methods_info = {
        'mpesa': {
            'name': 'M-Pesa',
            'instructions': [
                '1. Go to M-Pesa menu on your phone',
                '2. Select "Lipa na M-Pesa"',
                '3. Select "Pay Bill"',
                '4. Enter Business Number: 123456',
                '5. Enter Account Number: {}'.format(payment.transaction_reference),
                '6. Enter Amount: {}'.format(payment.amount),
                '7. Enter your M-Pesa PIN',
                '8. Confirm the transaction',
            ],
            'business_number': '123456',  # Replace with actual business number
        },
        'airtel_money': {
            'name': 'Airtel Money',
            'instructions': [
                '1. Dial *185# on your phone',
                '2. Select "Send Money"',
                '3. Enter recipient number: 123456',
                '4. Enter Amount: {}'.format(payment.amount),
                '5. Enter Reference: {}'.format(payment.transaction_reference),
                '6. Enter your PIN',
                '7. Confirm the transaction',
            ],
        },
        'mtn_mobile_money': {
            'name': 'MTN Mobile Money',
            'instructions': [
                '1. Dial *165# on your phone',
                '2. Select "Send Money"',
                '3. Enter recipient number: 123456',
                '4. Enter Amount: {}'.format(payment.amount),
                '5. Enter Reference: {}'.format(payment.transaction_reference),
                '6. Enter your PIN',
                '7. Confirm the transaction',
            ],
        },
        'tigo_pesa': {
            'name': 'Tigo Pesa',
            'instructions': [
                '1. Dial *150*11# on your phone',
                '2. Select "Send Money"',
                '3. Enter recipient number: 123456',
                '4. Enter Amount: {}'.format(payment.amount),
                '5. Enter Reference: {}'.format(payment.transaction_reference),
                '6. Enter your PIN',
                '7. Confirm the transaction',
            ],
        },
        'orange_money': {
            'name': 'Orange Money',
            'instructions': [
                '1. Dial #144# on your phone',
                '2. Select "Send Money"',
                '3. Enter recipient number: 123456',
                '4. Enter Amount: {}'.format(payment.amount),
                '5. Enter Reference: {}'.format(payment.transaction_reference),
                '6. Enter your PIN',
                '7. Confirm the transaction',
            ],
        },
        'mobile_money': {
            'name': 'Mobile Money',
            'instructions': [
                '1. Use your mobile money app or USSD code',
                '2. Send money to: 123456',
                '3. Amount: {}'.format(payment.amount),
                '4. Reference: {}'.format(payment.transaction_reference),
                '5. Complete the transaction',
            ],
        },
    }
    
    method_info = payment_methods_info.get(payment.payment_method, payment_methods_info['mobile_money'])
    # M-Pesa is STK push only – never show paybill steps
    use_stk_only = payment.payment_method == 'mpesa'
    review_url = reverse('subscriptions:review_subscription') + f'?plan={payment.plan_id}&billing_period={payment.billing_period}'
    context = {
        'payment': payment,
        'method_info': method_info,
        'transaction_ref': payment.transaction_reference,
        'use_stk_only': use_stk_only,
        'review_url': review_url,
    }
    return render(request, 'subscriptions/payment_instructions.html', context)


@login_required
def confirm_payment(request, payment_id):
    """User confirms payment with confirmation code."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if request.method == 'POST':
        confirmation_code = request.POST.get('confirmation_code', '').strip()
        
        if confirmation_code:
            payment.confirmation_code = confirmation_code
            payment.status = 'pending'  # Admin will verify
            payment.save()
            
            messages.success(request, "Payment confirmation received! Your subscription will be activated once we verify your payment (usually within 24 hours).")
            return redirect('subscriptions:manage')
        else:
            messages.error(request, "Please enter your confirmation code")
    
    context = {
        'payment': payment,
    }
    return render(request, 'subscriptions/confirm_payment.html', context)


@login_required
@require_POST
def cancel_subscription(request):
    """Cancel user's subscription."""
    if not hasattr(request.user, 'subscription'):
        messages.error(request, "No active subscription found")
        return redirect('subscriptions:manage')
    
    subscription = request.user.subscription
    subscription.auto_renew = False
    subscription.save()
    messages.success(request, "Subscription will be canceled at the end of the current billing period")
    
    return redirect('subscriptions:manage')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks (optional, for future use)."""
    # Placeholder for future Stripe integration if needed
    return HttpResponse(status=200)


@login_required
def verify_payment_admin(request, payment_id):
    """Admin function to verify and activate payment."""
    if not request.user.is_staff:
        messages.error(request, "Access denied")
        return redirect('core:home')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Mark payment as completed
            payment.status = 'completed'
            payment.save()
            
            # Check if this is a subscription payment or token purchase
            if payment.plan:
                # Subscription payment - create or update subscription
                billing_days = 30 if payment.billing_period == 'monthly' else 90 if payment.billing_period == 'quarterly' else 365
                subscription, created = Subscription.objects.get_or_create(
                    user=payment.user,
                    defaults={
                        'plan': payment.plan,
                        'billing_period': payment.billing_period,
                        'status': 'active',
                        'current_period_start': timezone.now(),
                        'current_period_end': timezone.now() + timedelta(days=billing_days),
                    }
                )
                
                if not created:
                    subscription.plan = payment.plan
                    subscription.billing_period = payment.billing_period
                    subscription.status = 'active'
                    subscription.current_period_start = timezone.now()
                    subscription.current_period_end = timezone.now() + timedelta(days=billing_days)
                    subscription.save()
                
                messages.success(request, f"Payment verified and subscription activated for {payment.user.username}")
            else:
                # Token purchase - add tokens to user account
                # Retrieve token amount from session or calculate from payment amount
                token_amount = int(payment.amount / settings.TOKEN_PRICE)
                token, created = Token.objects.get_or_create(user=payment.user)
                token.add_tokens(token_amount, reason=f'Purchased via {payment.payment_method}')
                messages.success(request, f"Payment verified and {token_amount} tokens added to {payment.user.username}")
            
            return redirect('admin:subscriptions_payment_changelist')
        
        elif action == 'reject':
            payment.status = 'failed'
            payment.save()
            messages.success(request, "Payment rejected")
            return redirect('admin:subscriptions_payment_changelist')
    
    context = {
        'payment': payment,
    }
    return render(request, 'subscriptions/admin_verify_payment.html', context)


# Token views
@login_required
def token_balance(request):
    """Display user's token balance."""
    token, created = Token.objects.get_or_create(user=request.user)
    
    context = {
        'token': token,
    }
    return render(request, 'subscriptions/tokens.html', context)


@login_required
def purchase_tokens(request):
    """Purchase tokens via mobile payment."""
    if request.method == 'POST':
        form = TokenPurchaseForm(request.POST)
        if form.is_valid():
            token_amount = int(form.cleaned_data['token_amount'])
            payment_method = form.cleaned_data['payment_method']
            phone_number = form.cleaned_data['phone_number']
            price = token_amount * settings.TOKEN_PRICE
            
            # Generate transaction reference
            transaction_ref = generate_transaction_reference()
            
            # Create pending payment
            payment = Payment.objects.create(
                user=request.user,
                plan=None,  # Token purchase doesn't need a plan
                amount=price,
                payment_method=payment_method,
                phone_number=phone_number,
                transaction_reference=transaction_ref,
                status='pending',
            )
            
            # Store token amount in payment metadata (we'll use a note field or create a separate model)
            # For now, we'll create a TokenPurchase record or use payment notes
            
            # Update user's phone number if provided
            if phone_number:
                request.user.phone_number = phone_number
                request.user.save(update_fields=['phone_number'])
            
            # Store token amount temporarily (we'll retrieve it when payment is verified)
            # Using a simple approach: store in a session or create TokenPurchase model
            request.session[f'token_purchase_{payment.id}'] = token_amount
            
            # Redirect to payment instructions
            return redirect('subscriptions:payment_instructions', payment_id=payment.id)
    else:
        form = TokenPurchaseForm()
    
    return render(request, 'subscriptions/purchase_tokens.html', {'form': form})


@login_required
def token_history(request):
    """View token transaction history."""
    transactions = TokenTransaction.objects.filter(user=request.user)[:50]
    
    context = {
        'transactions': transactions,
    }
    return render(request, 'subscriptions/token_history.html', context)


# Tip views
@login_required
def tip_creator(request, user_id):
    """Tip a creator."""
    from accounts.models import User
    
    creator = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = TipForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            message = form.cleaned_data.get('message', '')
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method == 'tokens':
                # Use tokens
                token, created = Token.objects.get_or_create(user=request.user)
                token_amount = int(amount / settings.TOKEN_PRICE)
                
                if token.spend_tokens(token_amount, f"Tip to {creator.username}"):
                    # Create tip
                    tip = Tip.objects.create(
                        from_user=request.user,
                        to_user=creator,
                        amount=amount,
                        message=message,
                        payment_method='tokens'
                    )
                    
                    # Create earning for creator
                    earning = CreatorEarning.objects.create(
                        creator=creator,
                        amount=amount,
                        revenue_type='tip',
                        platform_fee_percentage=settings.CREATOR_REVENUE_SHARE,
                    )
                    earning.calculate_earnings()
                    
                    messages.success(request, f"Tipped KSh {amount} to {creator.username}!")
                    return redirect('connections:user_profile', user_id=user_id)
                else:
                    messages.error(request, "Insufficient tokens")
            else:
                # Stripe payment
                try:
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'kes',
                                'product_data': {
                                    'name': f'Tip to {creator.username}',
                                },
                                'unit_amount': int(amount * 100),
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=request.build_absolute_uri(f'/connections/profile/{user_id}/') + '?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=request.build_absolute_uri(f'/connections/profile/{user_id}/'),
                        metadata={
                            'user_id': request.user.id,
                            'creator_id': creator.id,
                            'amount': str(amount),
                            'message': message,
                            'type': 'tip',
                        },
                    )
                    
                    return redirect(checkout_session.url)
                except stripe.error.StripeError as e:
                    messages.error(request, f"Payment error: {str(e)}")
    else:
        form = TipForm()
    
    context = {
        'creator': creator,
        'form': form,
    }
    return render(request, 'subscriptions/tip.html', context)


# Creator earnings
@login_required
def creator_earnings(request):
    """View creator earnings dashboard."""
    from subscriptions.models import CreatorEarning, Tip
    
    earnings = CreatorEarning.objects.filter(creator=request.user).order_by('-created_at')
    tips = Tip.objects.filter(to_user=request.user).order_by('-created_at')
    
    total_earnings = earnings.aggregate(total=Sum('creator_share'))['total'] or 0
    pending_earnings = earnings.filter(status='pending').aggregate(total=Sum('creator_share'))['total'] or 0
    available_earnings = earnings.filter(status='available').aggregate(total=Sum('creator_share'))['total'] or 0
    paid_earnings = earnings.filter(status='paid').aggregate(total=Sum('creator_share'))['total'] or 0
    
    context = {
        'earnings': earnings[:50],  # Last 50 earnings
        'tips': tips[:20],  # Last 20 tips
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'available_earnings': available_earnings,
        'paid_earnings': paid_earnings,
    }
    
    return render(request, 'subscriptions/creator_earnings.html', context)


# Pay-per-view
@login_required
def purchase_ppv(request, content_slug):
    """Purchase pay-per-view content."""
    content = get_object_or_404(Content, slug=content_slug)
    
    # Check if already purchased
    if PayPerViewPurchase.objects.filter(user=request.user, content=content).exists():
        messages.info(request, "You already own this content")
        return redirect('content:detail', slug=content_slug)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'tokens')
        amount = content.ppv_price if hasattr(content, 'ppv_price') else 650.00  # Default KSh 650
        
        if payment_method == 'tokens':
            token, created = Token.objects.get_or_create(user=request.user)
            token_amount = int(amount / settings.TOKEN_PRICE)
            
            if token.spend_tokens(token_amount, f"PPV: {content.title}"):
                PayPerViewPurchase.objects.create(
                    user=request.user,
                    content=content,
                    amount=amount,
                    payment_method='tokens'
                )
                
                # Create earning for creator
                earning = CreatorEarning.objects.create(
                    creator=content.uploader,
                    content=content,
                    amount=amount,
                    revenue_type='pay_per_view',
                    platform_fee_percentage=100 - settings.CREATOR_REVENUE_SHARE,
                )
                earning.calculate_earnings()
                
                messages.success(request, "Content purchased successfully!")
                return redirect('content:detail', slug=content_slug)
            else:
                messages.error(request, "Insufficient tokens")
        else:
            # Stripe payment
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'kes',
                            'product_data': {
                                'name': content.title,
                            },
                            'unit_amount': int(amount * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/content/{content_slug}/') + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(f'/content/{content_slug}/'),
                    metadata={
                        'user_id': request.user.id,
                        'content_id': content.id,
                        'amount': str(amount),
                        'type': 'ppv',
                    },
                )
                
                return redirect(checkout_session.url)
            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {str(e)}")
    
    context = {
        'content': content,
        'ppv_price': getattr(content, 'ppv_price', 5.00),
    }
    return render(request, 'subscriptions/purchase_ppv.html', context)
