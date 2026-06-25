"""
M-Pesa callback (Daraja posts here), local status poll, and helpers.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import MpesaTransaction
from .services.activation import activate_payment_for_transaction
from .services.c2b import handle_c2b_confirmation, handle_c2b_validation, try_match_pending_c2b_for_payment
from .services.errors import humanize_stk_failure

logger = logging.getLogger(__name__)


def _normalize_result_code(value):
    try:
        return int(value) if value not in (None, '') else -1
    except (TypeError, ValueError):
        return -1


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def mpesa_callback(request):
    """
    GET: health check — verify this URL is reachable from the internet.
    POST: Daraja STK Push result (Body.stkCallback).
    """
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'endpoint': 'payments/mpesa/callback/',
            'message': 'M-Pesa callback URL is reachable. Safaricom Daraja POSTs STK results here.',
            'accepts': 'POST',
        })

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
    result_code = _normalize_result_code(stk.get('ResultCode'))
    result_desc = stk.get('ResultDesc', '')

    if not checkout_request_id:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Missing CheckoutRequestID'}, status=400)

    try:
        txn = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
    except MpesaTransaction.DoesNotExist:
        logger.warning('M-Pesa callback unknown CheckoutRequestID: %s', checkout_request_id)
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

    meta = stk.get('CallbackMetadata', {})
    meta_list = meta.get('Item', [])
    receipt_number = ''
    for item in meta_list:
        if item.get('Name') == 'MpesaReceiptNumber':
            receipt_number = str(item.get('Value', ''))

    txn.result_code = result_code
    txn.result_description = result_desc
    txn.callback_metadata = stk
    txn.mpesa_receipt_number = receipt_number
    txn.status = 'completed' if result_code == 0 else 'failed'
    txn.save(update_fields=[
        'status', 'result_code', 'result_description', 'callback_metadata',
        'mpesa_receipt_number', 'updated_at',
    ])

    logger.info(
        '[mpesa_callback] checkout=%s result_code=%s status=%s',
        checkout_request_id[:24], result_code, txn.status,
    )

    if result_code == 0:
        activate_payment_for_transaction(txn)

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})


def _mpesa_status_response(data):
    return JsonResponse(data)


@login_required
@require_GET
def mpesa_status(request, payment_id):
    """
    Poll local DB (updated by Daraja callback).
    If still pending after 30s, run one Daraja STK query as fallback (rate-limited per transaction).
    """
    from django.core.cache import cache
    from django.utils import timezone
    from subscriptions.models import Payment
    from .services.mpesa import MpesaService
    from .services.reconcile import apply_stk_query_result

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status == 'completed':
        return _mpesa_status_response({
            'status': 'completed',
            'paid': True,
            'message': 'Payment confirmed',
        })

    if payment.payment_method == 'mpesa_till':
        try_match_pending_c2b_for_payment(payment)
        payment.refresh_from_db()
        if payment.status == 'completed':
            return _mpesa_status_response({
                'status': 'completed',
                'paid': True,
                'message': 'Payment confirmed',
            })
        return _mpesa_status_response({
            'status': 'pending',
            'paid': False,
            'message': 'Waiting for M-Pesa till payment confirmation…',
        })

    if payment.payment_method != 'mpesa':
        return _mpesa_status_response({
            'status': 'failed',
            'paid': False,
            'message': 'Not an M-Pesa payment',
        })

    account_ref = f'sub_{payment.id}'
    try:
        txn = MpesaTransaction.objects.get(account_reference=account_ref)
    except MpesaTransaction.DoesNotExist:
        return _mpesa_status_response({
            'status': 'failed',
            'paid': False,
            'message': 'Transaction not found',
        })

    if txn.status == 'completed':
        activate_payment_for_transaction(txn)
        payment.refresh_from_db()
        if payment.status == 'completed':
            return _mpesa_status_response({
                'status': 'completed',
                'paid': True,
                'message': 'Payment confirmed',
            })

    if txn.status in ('failed', 'cancelled'):
        return _mpesa_status_response({
            'status': 'failed',
            'paid': False,
            'message': humanize_stk_failure(txn.result_code, txn.result_description),
        })

    # Fallback: one STK query per transaction every 2 minutes if callback not received
    if txn.checkout_request_id:
        age_seconds = (timezone.now() - txn.created_at).total_seconds()
        reconcile_key = f'mpesa_status_reconcile_{txn.id}'
        if age_seconds >= 30 and not cache.get(reconcile_key):
            cache.set(reconcile_key, True, 120)
            result = MpesaService().query_stk_push(txn.checkout_request_id)
            apply_stk_query_result(txn, result)
            txn.refresh_from_db()
            payment.refresh_from_db()
            if payment.status == 'completed' or txn.status == 'completed':
                return _mpesa_status_response({
                    'status': 'completed',
                    'paid': True,
                    'message': 'Payment confirmed',
                })
            if txn.status == 'failed':
                return _mpesa_status_response({
                    'status': 'failed',
                    'paid': False,
                    'message': humanize_stk_failure(txn.result_code, txn.result_description),
                })

    return _mpesa_status_response({
        'status': 'pending',
        'paid': False,
        'message': 'Waiting for you to enter your M-Pesa PIN on your phone…',
    })


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def c2b_validation(request):
    """Daraja C2B validation callback — must respond quickly with Accept."""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'endpoint': 'payments/c2b/validation/',
            'message': 'C2B validation URL is reachable.',
        })
    try:
        body = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)
    return JsonResponse(handle_c2b_validation(body))


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def c2b_confirmation(request):
    """Daraja C2B confirmation — payment received on till/paybill."""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'endpoint': 'payments/c2b/confirmation/',
            'message': 'C2B confirmation URL is reachable.',
        })
    try:
        body = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)
    return JsonResponse(handle_c2b_confirmation(body))
