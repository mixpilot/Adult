"""
Activate subscriptions (and future payment types) after a successful M-Pesa transaction.
"""
import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def activate_payment_for_transaction(txn) -> bool:
    """
    Map account_reference to subscription and activate.
    Idempotent: no-op if payment already completed.

    Returns True if payment was activated (or was already completed).
    """
    ref = (txn.account_reference or '').strip()
    if not ref.startswith('sub_'):
        return False

    try:
        payment_id = ref.replace('sub_', '')
        from subscriptions.models import Payment, Subscription

        payment = Payment.objects.filter(id=int(payment_id)).select_related('user', 'plan').first()
        if not payment:
            logger.warning('M-Pesa activation: payment %s not found for ref %s', payment_id, ref)
            return False
        if payment.status == 'completed':
            return True

        payment.status = 'completed'
        payment.transaction_reference = txn.mpesa_receipt_number or txn.checkout_request_id
        payment.save(update_fields=['status', 'transaction_reference', 'updated_at'])

        user = payment.user
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified'])

        plan = payment.plan
        billing_days = (
            30 if payment.billing_period in ('monthly', 'once')
            else 90 if payment.billing_period == 'quarterly'
            else 365
        )
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
        if payment.billing_period == 'once':
            subscription.auto_renew = False
            subscription.save(update_fields=['auto_renew'])

        logger.info(
            'Subscription activated for payment %s (M-Pesa %s), user verified=%s',
            payment_id, txn.mpesa_receipt_number, user.is_verified,
        )
        return True
    except (ValueError, TypeError) as e:
        logger.exception('Could not activate subscription for M-Pesa ref %s: %s', ref, e)
        return False
