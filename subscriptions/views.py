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
from .billing import billing_days_for_period
from .models import (
    SubscriptionPlan, Subscription, Payment, PromoCode,
    Token, TokenTransaction, CreatorEarning, PayPerViewPurchase, Tip
)
from .forms import SubscriptionForm, PromoCodeForm, TokenPurchaseForm, TipForm
from content.models import Content


def ensure_default_plans():
    """Create Daily (150), Weekly (200), Premium monthly (500) for clients and escorts."""
    if SubscriptionPlan.objects.filter(
        tier__in=('daily', 'weekly', 'premium'), user_type='both', is_active=True,
    ).count() >= 3:
        return
    plans_data = [
        {
            'tier': 'daily', 'user_type': 'both', 'name': 'Daily', 'price_monthly': Decimal('150.00'),
            'description': 'Full access for 24 hours. For clients and escorts.',
            'unlimited_messaging': True, 'unlimited_content_access': True, 'advanced_search': True,
        },
        {
            'tier': 'weekly', 'user_type': 'both', 'name': 'Weekly', 'price_monthly': Decimal('200.00'),
            'description': 'Full access for 7 days. For clients and escorts.',
            'unlimited_messaging': True, 'unlimited_content_access': True, 'advanced_search': True,
        },
        {
            'tier': 'premium', 'user_type': 'both', 'name': 'Premium', 'price_monthly': Decimal('500.00'),
            'description': 'Premium monthly access with ad-free experience and priority support.',
            'unlimited_messaging': True, 'unlimited_content_access': True,
            'ad_free': True, 'advanced_search': True, 'priority_support': True,
        },
    ]
    for d in plans_data:
        SubscriptionPlan.objects.update_or_create(
            tier=d['tier'], user_type=d['user_type'],
            defaults={k: v for k, v in d.items() if k not in ('tier', 'user_type')},
        )
    SubscriptionPlan.objects.filter(tier__in=('basic', 'once')).update(is_active=False)


@login_required
def subscription_plans(request):
    """Display subscription plans based on user type."""
    ensure_default_plans()
    user_type = request.user.user_type
    is_new_user = request.GET.get('new_user') == '1'
    
    plans = list(
        SubscriptionPlan.objects.filter(is_active=True)
        .filter(models.Q(user_type=user_type) | models.Q(user_type='both'))
        .filter(tier__in=('daily', 'weekly', 'premium'))
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
    # Fixed billing period per plan tier (daily / weekly / monthly)
    if getattr(plan, 'is_one_time_plan', plan.tier == 'once'):
        billing_period = 'once'
    elif plan.tier in ('daily', 'weekly', 'premium'):
        billing_period = plan.default_billing_period
    else:
        billing_period = request.GET.get('billing_period', plan.default_billing_period)
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
        'is_fixed_period_plan': getattr(plan, 'is_fixed_period_plan', plan.tier in ('daily', 'weekly', 'premium', 'once')),
        'mpesa_till_number': getattr(settings, 'MPESA_TILL_NUMBER', '') or getattr(settings, 'MPESA_SHORTCODE', ''),
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

    billing_period = plan.default_billing_period if plan.tier in ('daily', 'weekly', 'premium', 'once') else billing_period

    if request.method != 'POST':
        logger.warning('[subscribe] REDIRECT → review (method not POST)')
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    # POST: payment details
    payment_method = request.POST.get('payment_method')
    phone_number = request.POST.get('phone_number', '').strip()
    logger.warning('[subscribe] payment_method=%r phone_number=%r', payment_method, phone_number or '(empty)')

    allowed_methods = ('mpesa', 'mpesa_till')
    if payment_method not in allowed_methods:
        messages.error(request, 'Please choose M-Pesa STK Push or Pay to Till.')
        return redirect(f"{reverse('subscriptions:review_subscription')}?plan={plan_id}&billing_period={billing_period}")

    if payment_method == 'mpesa' and not phone_number:
        messages.error(request, 'Enter your M-Pesa phone number for STK Push.')
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

    # Pay to Till: show instructions, then user submits M-Pesa receipt code
    if payment_method == 'mpesa_till':
        return redirect('subscriptions:till_payment', payment_id=payment.id)

    # M-Pesa STK Push
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
    if payment.payment_method == 'mpesa_till':
        return redirect('subscriptions:till_payment', payment_id=payment_id)
    if payment.payment_method != 'mpesa':
        return redirect('subscriptions:manage')
    if payment.status == 'completed':
        messages.success(request, 'Payment completed. Your subscription is active.')
        return redirect('subscriptions:manage')
    context = {'payment': payment}
    return render(request, 'subscriptions/mpesa_waiting.html', context)


@login_required
def payment_instructions(request, payment_id):
    """Till payment instructions, or STK retry page for failed mpesa."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.payment_method == 'mpesa_till':
        return till_payment(request, payment_id)

    review_url = reverse('subscriptions:review_subscription') + f'?plan={payment.plan_id}&billing_period={payment.billing_period}'
    return render(request, 'subscriptions/payment_instructions.html', {
        'payment': payment,
        'review_url': review_url,
    })


@login_required
def till_payment(request, payment_id):
    """Pay directly to M-Pesa till, then submit receipt code."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    till_number = getattr(settings, 'MPESA_TILL_NUMBER', '') or getattr(settings, 'MPESA_SHORTCODE', '')
    return render(request, 'subscriptions/till_payment.html', {
        'payment': payment,
        'till_number': till_number,
        'transaction_ref': payment.transaction_reference,
    })


def _normalize_mpesa_receipt(code: str) -> str:
    return ''.join(c for c in (code or '').strip().upper() if c.isalnum())


def _verify_till_receipt_code(code: str, payment: Payment):
    """Validate M-Pesa receipt/confirmation code for till payments."""
    from payments.models import MpesaTransaction

    normalized = _normalize_mpesa_receipt(code)
    if len(normalized) < 8:
        return False, 'Enter the full M-Pesa confirmation code from your SMS (e.g. THJ4ABC12X).'

    if Payment.objects.filter(
        confirmation_code__iexact=normalized,
        status='completed',
    ).exclude(id=payment.id).exists():
        return False, 'This M-Pesa code has already been used for another subscription.'

    if MpesaTransaction.objects.filter(
        mpesa_receipt_number__iexact=normalized,
        status='completed',
    ).exists():
        return False, 'This M-Pesa code is already linked to a completed payment.'

    return True, normalized


@login_required
def confirm_payment(request, payment_id):
    """User submits M-Pesa receipt code; verify via C2B record if available."""
    from payments.services.c2b import verify_receipt_for_payment

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status == 'completed':
        messages.info(request, 'This payment is already completed.')
        return redirect('subscriptions:manage')

    if request.method == 'POST':
        raw_code = request.POST.get('confirmation_code', '')
        ok, result = _verify_till_receipt_code(raw_code, payment)
        if not ok:
            messages.error(request, result)
        else:
            activated, msg = verify_receipt_for_payment(payment, result)
            if activated:
                messages.success(request, msg)
                return redirect('subscriptions:manage')
            messages.info(
                request,
                'Code saved. If payment is not activated within a minute, we are still waiting for '
                'M-Pesa confirmation — refresh your subscription page shortly.',
            )
            return redirect('subscriptions:manage')

    context = {
        'payment': payment,
        'till_number': getattr(settings, 'MPESA_TILL_NUMBER', '') or getattr(settings, 'MPESA_SHORTCODE', ''),
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
                billing_days = billing_days_for_period(payment.billing_period)
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
