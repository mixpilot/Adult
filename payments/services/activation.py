"""
Activate subscriptions after successful M-Pesa payment (STK or C2B).
"""
import logging
from datetime import timedelta

from django.utils import timezone

from subscriptions.billing import billing_days_for_period

logger = logging.getLogger(__name__)


def activate_subscription_payment(payment, receipt_id: str = '') -> bool:
    """
    Mark Payment completed and activate/update Subscription.
    Idempotent if payment already completed.
    """
    if payment.status == 'completed':
        return True

    payment.status = 'completed'
    if receipt_id:
        payment.transaction_reference = receipt_id
        payment.confirmation_code = receipt_id
    payment.save(update_fields=['status', 'transaction_reference', 'confirmation_code', 'updated_at'])

    user = payment.user
    if not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])

    from subscriptions.models import Subscription

    plan = payment.plan
    billing_days = billing_days_for_period(payment.billing_period)
    subscription, created = Subscription.objects.get_or_create(
        user=payment.user,
        defaults={
            'plan': plan,
            'billing_period': payment.billing_period,
            'status': 'active',
            'current_period_start': timezone.now(),
            'current_period_end': timezone.now() + timedelta(days=billing_days),
        },
    )
    if not created:
        subscription.plan = plan
        subscription.billing_period = payment.billing_period
        subscription.status = 'active'
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = timezone.now() + timedelta(days=billing_days)
        subscription.save()
    if payment.billing_period in ('once', 'daily', 'weekly'):
        subscription.auto_renew = False
        subscription.save(update_fields=['auto_renew'])

    logger.info(
        'Subscription activated for payment %s (receipt %s), user verified=%s',
        payment.id, receipt_id, user.is_verified,
    )
    return True


def activate_payment_for_transaction(txn) -> bool:
    """Map STK MpesaTransaction account_reference to subscription payment."""
    ref = (txn.account_reference or '').strip()
    if not ref.startswith('sub_'):
        return False

    try:
        payment_id = int(ref.replace('sub_', ''))
        from subscriptions.models import Payment

        payment = Payment.objects.filter(id=payment_id).select_related('user', 'plan').first()
        if not payment:
            logger.warning('M-Pesa activation: payment %s not found for ref %s', payment_id, ref)
            return False

        receipt = txn.mpesa_receipt_number or txn.checkout_request_id
        return activate_subscription_payment(payment, receipt_id=receipt)
    except (ValueError, TypeError) as e:
        logger.exception('Could not activate subscription for M-Pesa ref %s: %s', ref, e)
        return False
