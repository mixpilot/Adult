"""
Background reconciliation: query Daraja for pending STK transactions that missed the callback.
"""
import logging
from datetime import timedelta

from django.utils import timezone

from payments.models import MpesaTransaction
from payments.services.activation import activate_payment_for_transaction
from payments.services.errors import humanize_stk_failure
from payments.services.mpesa import MpesaService

logger = logging.getLogger(__name__)


def apply_stk_query_result(txn: MpesaTransaction, result: dict) -> str:
    """
    Update a transaction from Daraja STK query response.

    Returns: 'completed', 'failed', 'pending', or 'error' (retry later).
    """
    if result.get('success'):
        txn.status = 'completed'
        txn.result_code = result.get('result_code', 0)
        txn.result_description = (result.get('result_desc') or '')[:512]
        txn.mpesa_receipt_number = (result.get('mpesa_receipt_number') or '')[:50]
        txn.save(update_fields=[
            'status', 'result_code', 'result_description', 'mpesa_receipt_number', 'updated_at',
        ])
        activate_payment_for_transaction(txn)
        return 'completed'

    result_code = result.get('result_code', -1)
    if result_code == -1:
        return 'error'

    # Any definitive non-zero ResultCode from query is terminal (incl. 2029, 1032, 1037, 1).
    if result_code > 0:
        txn.status = 'failed'
        txn.result_code = result_code
        desc = (result.get('result_desc') or result.get('error_message') or '')[:512]
        txn.result_description = humanize_stk_failure(result_code, desc)[:512]
        txn.save(update_fields=['status', 'result_code', 'result_description', 'updated_at'])
        return 'failed'

    return 'pending'


def reconcile_pending_transactions(min_age_seconds: int = 90, limit: int = 20) -> dict:
    """
    Query Daraja for pending transactions older than min_age_seconds.
    Intended for cron: python manage.py reconcile_mpesa

    Returns summary counts.
    """
    cutoff = timezone.now() - timedelta(seconds=min_age_seconds)
    pending = MpesaTransaction.objects.filter(
        status='pending',
        checkout_request_id__gt='',
        created_at__lte=cutoff,
    ).order_by('created_at')[:limit]

    service = MpesaService()
    summary = {'checked': 0, 'completed': 0, 'failed': 0, 'pending': 0, 'errors': 0}

    for txn in pending:
        summary['checked'] += 1
        result = service.query_stk_push(txn.checkout_request_id)
        outcome = apply_stk_query_result(txn, result)
        summary[outcome if outcome in summary else 'errors'] += 1
        logger.info(
            '[mpesa_reconcile] %s checkout=%s outcome=%s result_code=%s',
            txn.account_reference,
            (txn.checkout_request_id or '')[:24],
            outcome,
            result.get('result_code'),
        )

    return summary
