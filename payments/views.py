"""
M-Pesa callback (Daraja posts here), status poll (when no callback URL), and helpers.
"""
import json
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET

from .models import MpesaTransaction
from .services import PaystackService

logger = logging.getLogger(__name__)


def activate_payment(payment, provider_reference=''):
    """
    Mark payment as completed and activate subscription if this is a subscription payment.
    """
    from subscriptions.models import Subscription

    update_fields = []
    if payment.status != 'completed':
        payment.status = 'completed'
        update_fields.append('status')

    if provider_reference:
        payment.transaction_reference = provider_reference
        update_fields.append('transaction_reference')

    if update_fields:
        update_fields.append('updated_at')
        payment.save(update_fields=update_fields)

    # Non-subscription payment (tokens/tips/ppv) can be handled separately later.
    if not payment.plan:
        return

    # After successful payment, mark user verified so they can access escorts.
    user = payment.user
    if not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])

    billing_days = (
        30 if payment.billing_period in ('monthly', 'once')
        else 90 if payment.billing_period == 'quarterly'
        else 365
    )
    subscription, created = Subscription.objects.get_or_create(
        user=payment.user,
        defaults={
            'plan': payment.plan,
            'billing_period': payment.billing_period,
            'status': 'active',
            'current_period_start': timezone.now(),
            'current_period_end': timezone.now() + timedelta(days=billing_days),
        },
    )
    if not created:
        subscription.plan = payment.plan
        subscription.billing_period = payment.billing_period
        subscription.status = 'active'
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = timezone.now() + timedelta(days=billing_days)
        subscription.save()

    if payment.billing_period == 'once':
        subscription.auto_renew = False
        subscription.save(update_fields=['auto_renew'])


@csrf_exempt
@require_http_methods(['POST'])
def mpesa_callback(request):
    """
    Daraja API calls this with STK Push result.
    Body: JSON with Body.stkCallback (CheckoutRequestID, ResultCode, ResultDesc, CallbackMetadata).
    """
    try:
        body = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning('M-Pesa callback invalid JSON: %s', e)
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)

    stk = body.get('Body', {}).get('stkCallback')
    if not stk:
        logger.warning('M-Pesa callback missing Body.stkCallback')
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Missing stkCallback'}, status=400)

    checkout_request_id = stk.get('CheckoutRequestID')
    merchant_request_id = stk.get('MerchantRequestID')
    result_code = stk.get('ResultCode')
    result_desc = stk.get('ResultDesc', '')

    if not checkout_request_id:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Missing CheckoutRequestID'}, status=400)

    try:
        txn = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
    except MpesaTransaction.DoesNotExist:
        logger.warning('M-Pesa callback unknown CheckoutRequestID: %s', checkout_request_id)
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

    # Parse callback metadata (amount, receipt, etc.)
    meta = stk.get('CallbackMetadata', {})
    meta_list = meta.get('Item', [])
    receipt_number = ''
    amount = None
    for item in meta_list:
        if item.get('Name') == 'MpesaReceiptNumber':
            receipt_number = str(item.get('Value', ''))
        if item.get('Name') == 'Amount':
            amount = item.get('Value')

    txn.result_code = result_code
    txn.result_description = result_desc
    txn.callback_metadata = stk
    txn.mpesa_receipt_number = receipt_number
    if result_code == 0:
        txn.status = 'completed'
    else:
        txn.status = 'failed'
    txn.save(update_fields=[
        'status', 'result_code', 'result_description', 'callback_metadata',
        'mpesa_receipt_number', 'updated_at',
    ])

    if result_code == 0:
        # Activate subscription (or other payment type) based on account_reference
        _handle_successful_payment(txn)

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})


def _handle_successful_payment(txn: MpesaTransaction):
    """
    Map account_reference to subscription (or future: tokens, etc.) and activate.
    account_reference format: sub_<payment_id> for subscription.
    """
    ref = (txn.account_reference or '').strip()
    if ref.startswith('sub_'):
        try:
            payment_id = ref.replace('sub_', '')
            from subscriptions.models import Payment

            payment = Payment.objects.get(id=int(payment_id), status='pending')
            activate_payment(payment, provider_reference=txn.mpesa_receipt_number or txn.checkout_request_id)
            logger.info('Subscription activated for payment %s (M-Pesa %s)', payment_id, txn.mpesa_receipt_number)
        except (ValueError, Payment.DoesNotExist) as e:
            logger.exception('Could not activate subscription for M-Pesa ref %s: %s', ref, e)


def _mpesa_status_response(data):
    """Log and return JsonResponse for status endpoint."""
    logger.warning('[mpesa_status] 200 response: %s', data)
    return JsonResponse(data)


@login_required
@require_GET
def mpesa_status(request, payment_id):
    """
    Poll this to check if an M-Pesa payment has completed (when you don't use a callback URL).
    Queries Daraja STK Push Query API and, on success, updates Payment to completed and activates subscription.
    Returns JSON: { "status": "completed"|"pending"|"failed", "paid": true|false, "message": "..." }
    """
    from subscriptions.models import Payment
    from .services import MpesaService

    logger.warning('[mpesa_status] GET payment_id=%s', payment_id)
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    if payment.status == 'completed':
        return _mpesa_status_response({'status': 'completed', 'paid': True, 'message': 'Already paid'})

    if payment.payment_method != 'mpesa':
        return _mpesa_status_response({'status': 'failed', 'paid': False, 'message': 'Not an M-Pesa payment'})

    account_ref = f'sub_{payment.id}'
    try:
        txn = MpesaTransaction.objects.get(account_reference=account_ref)
    except MpesaTransaction.DoesNotExist:
        return _mpesa_status_response({'status': 'failed', 'paid': False, 'message': 'Transaction not found'})

    if txn.status == 'completed':
        _handle_successful_payment(txn)
        return _mpesa_status_response({'status': 'completed', 'paid': True, 'message': 'Payment confirmed'})

    if not txn.checkout_request_id:
        return _mpesa_status_response({'status': 'failed', 'paid': False, 'message': 'No checkout request ID'})

    service = MpesaService()
    result = service.query_stk_push(txn.checkout_request_id)
    logger.warning('[mpesa_status] query_stk_push result: success=%s result_code=%s rate_limit=%s',
                   result.get('success'), result.get('result_code'), result.get('rate_limit'))

    if result.get('success'):
        txn.status = 'completed'
        txn.result_code = result.get('result_code', 0)
        txn.result_description = result.get('result_desc', '')[:512]
        txn.mpesa_receipt_number = result.get('mpesa_receipt_number', '')[:50]
        txn.save(update_fields=['status', 'result_code', 'result_description', 'mpesa_receipt_number', 'updated_at'])
        _handle_successful_payment(txn)
        return _mpesa_status_response({'status': 'completed', 'paid': True, 'message': 'Payment confirmed'})

    result_code = result.get('result_code', -1)
    if result_code == -1:
        return _mpesa_status_response({
            'status': 'pending',
            'paid': False,
            'message': result.get('error_message') or 'Checking again…',
            'rate_limit': result.get('rate_limit', False),
        })

    if result_code in (1032, 1037, 1):
        txn.status = 'failed'
        txn.result_code = result_code
        txn.result_description = result.get('result_desc', '')[:512]
        txn.save(update_fields=['status', 'result_code', 'result_description', 'updated_at'])
        return _mpesa_status_response({
            'status': 'failed',
            'paid': False,
            'message': result.get('result_desc') or result.get('error_message', 'Payment failed or cancelled'),
        })

    return _mpesa_status_response({
        'status': 'pending',
        'paid': False,
        'message': result.get('result_desc') or 'Waiting for payment on your phone.',
    })


@require_GET
def paystack_callback(request):
    """
    Browser return URL from Paystack hosted checkout.
    """
    from subscriptions.models import Payment

    reference = (request.GET.get('reference') or request.GET.get('trxref') or '').strip()
    if not reference:
        messages.error(request, 'Missing Paystack reference.')
        return redirect('subscriptions:plans')

    payment = Payment.objects.filter(transaction_reference=reference).first()
    if not payment:
        messages.error(request, 'Payment not found for this reference.')
        return redirect('subscriptions:plans')

    service = PaystackService()
    result = service.verify_transaction(reference)
    if not result.get('success'):
        logger.warning('[paystack] verify failed reference=%s error=%s', reference, result.get('error_message'))
        messages.error(request, result.get('error_message') or 'Could not verify payment. Please try again.')
        return redirect('subscriptions:manage')

    if result.get('paid'):
        activate_payment(payment, provider_reference=result.get('reference') or reference)
        messages.success(request, 'Payment confirmed. Your subscription is active.')
    else:
        payment.status = 'failed'
        payment.save(update_fields=['status', 'updated_at'])
        messages.error(request, result.get('error_message') or 'Payment was not completed.')

    return redirect('subscriptions:manage')
