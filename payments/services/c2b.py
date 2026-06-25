"""
M-Pesa C2B: register URLs, validation/confirmation callbacks, match till payments.
"""
import json
import logging
from decimal import Decimal, InvalidOperation
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from payments.models import C2bTransaction
from payments.services.activation import activate_subscription_payment
from payments.services.mpesa import MpesaService, _DEFAULT_HEADERS

logger = logging.getLogger(__name__)


def _normalize_phone(phone: str) -> str:
    return MpesaService().normalize_phone(phone or '')


def _parse_amount(value) -> Decimal:
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')


def c2b_urls():
    base = getattr(settings, 'MPESA_CALLBACK_BASE_URL', '').rstrip('/')
    # Daraja C2B register rejects URLs containing "mpesa" (case-insensitive).
    return {
        'validation': f'{base}/payments/c2b/validation/',
        'confirmation': f'{base}/payments/c2b/confirmation/',
    }


def register_c2b_urls() -> dict:
    """Register validation + confirmation URLs with Daraja (run once per shortcode)."""
    service = MpesaService()
    shortcode = getattr(settings, 'MPESA_C2B_SHORTCODE', None) or settings.MPESA_SHORTCODE
    urls = c2b_urls()
    token = service._get_access_token()
    # Production apps with C2B v2 product must use v2; v1 returns 401.003.01 (misleading "Invalid Access Token").
    api_version = getattr(settings, 'MPESA_C2B_API_VERSION', None)
    if not api_version:
        api_version = 'v2' if service.env == 'production' else 'v1'
    api_url = f'{service._base_url}/mpesa/c2b/{api_version}/registerurl'
    payload = {
        'ShortCode': str(shortcode),
        'ResponseType': 'Completed',
        'ConfirmationURL': urls['confirmation'],
        'ValidationURL': urls['validation'],
    }
    req = Request(
        api_url,
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            **_DEFAULT_HEADERS,
        },
        method='POST',
    )
    logger.info(
        '[c2b] register shortcode=%s api=%s validation=%s confirmation=%s',
        shortcode, api_version, urls['validation'], urls['confirmation'],
    )
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            logger.info('[c2b] register response: %s', data)
            return {'success': True, 'data': data}
    except HTTPError as e:
        body = e.read().decode(errors='replace') if e.fp else ''
        logger.error('[c2b] register HTTP %s: %s', e.code, body)
        return {'success': False, 'error': body or str(e)}
    except (URLError, json.JSONDecodeError) as e:
        logger.exception('[c2b] register failed: %s', e)
        return {'success': False, 'error': str(e)}


def handle_c2b_validation(body: dict) -> dict:
    """Accept all incoming C2B validation requests."""
    logger.info('[c2b_validation] TransID=%s amount=%s msisdn=%s', body.get('TransID'), body.get('TransAmount'), body.get('MSISDN'))
    return {'ResultCode': 0, 'ResultDesc': 'Accepted'}


def _find_pending_payment(c2b: C2bTransaction):
    """Match a C2B notification to a pending till subscription payment."""
    from subscriptions.models import Payment

    trans_id = c2b.trans_id.upper()
    amount = c2b.trans_amount
    phone = _normalize_phone(c2b.msisdn)
    cutoff = timezone.now() - timedelta(hours=6)

    # User already submitted this receipt code
    by_code = Payment.objects.filter(
        payment_method='mpesa_till',
        status='pending',
        confirmation_code__iexact=trans_id,
    ).first()
    if by_code:
        return by_code

    # Bill reference matches our transaction ref (paybill) or sub_<id>
    bill = (c2b.bill_ref_number or '').strip()
    if bill:
        by_ref = Payment.objects.filter(
            payment_method='mpesa_till',
            status='pending',
            transaction_reference__iexact=bill,
        ).first()
        if by_ref:
            return by_ref
        if bill.lower().startswith('sub_'):
            try:
                pid = int(bill.replace('sub_', '').split('-')[0])
                by_sub = Payment.objects.filter(id=pid, status='pending', payment_method='mpesa_till').first()
                if by_sub:
                    return by_sub
            except (ValueError, TypeError):
                pass

    # Amount + phone + recent pending till payment
    candidates = Payment.objects.filter(
        payment_method='mpesa_till',
        status='pending',
        amount=amount,
        created_at__gte=cutoff,
    ).order_by('created_at')

    for payment in candidates:
        pay_phone = _normalize_phone(payment.phone_number or '')
        if pay_phone and phone and pay_phone == phone:
            return payment

    # Amount only (single open pending at this amount)
    if candidates.count() == 1:
        return candidates.first()

    return None


def try_activate_c2b_payment(c2b: C2bTransaction) -> bool:
    """Link C2B to a subscription payment and activate if possible."""
    if c2b.payment_id:
        payment = c2b.payment
        if payment.status == 'completed':
            return True
    else:
        payment = _find_pending_payment(c2b)
        if not payment:
            logger.info('[c2b] no matching pending payment for %s', c2b.trans_id)
            return False
        c2b.payment = payment
        c2b.save(update_fields=['payment'])

    if payment.amount != c2b.trans_amount:
        logger.warning(
            '[c2b] amount mismatch payment=%s c2b=%s trans_id=%s',
            payment.amount, c2b.trans_amount, c2b.trans_id,
        )
        return False

    return activate_subscription_payment(payment, receipt_id=c2b.trans_id)


def try_match_pending_c2b_for_payment(payment) -> bool:
    """Poll path: match an unlinked C2B record to a pending till payment."""
    if payment.status == 'completed' or payment.payment_method != 'mpesa_till':
        return payment.status == 'completed'

    code = (payment.confirmation_code or '').strip()
    if code:
        c2b = C2bTransaction.objects.filter(trans_id__iexact=code).first()
        if c2b:
            return try_activate_c2b_payment(c2b)

    cutoff = timezone.now() - timedelta(hours=6)
    phone = _normalize_phone(payment.phone_number or '')
    candidates = C2bTransaction.objects.filter(
        payment__isnull=True,
        trans_amount=payment.amount,
        created_at__gte=cutoff,
    ).order_by('-created_at')

    for c2b in candidates:
        c2b_phone = _normalize_phone(c2b.msisdn)
        if phone and c2b_phone and phone == c2b_phone:
            return try_activate_c2b_payment(c2b)

    if candidates.count() == 1:
        return try_activate_c2b_payment(candidates.first())

    return False


def handle_c2b_confirmation(body: dict) -> dict:
    """Process C2B confirmation callback from Safaricom."""
    trans_id = (body.get('TransID') or '').strip().upper()
    if not trans_id:
        logger.warning('[c2b_confirmation] missing TransID')
        return {'ResultCode': 0, 'ResultDesc': 'Success'}

    c2b, created = C2bTransaction.objects.get_or_create(
        trans_id=trans_id,
        defaults={
            'trans_amount': _parse_amount(body.get('TransAmount')),
            'trans_time': str(body.get('TransTime', '')),
            'business_shortcode': str(body.get('BusinessShortCode', '')),
            'bill_ref_number': str(body.get('BillRefNumber', '')),
            'msisdn': str(body.get('MSISDN', '')),
            'transaction_type': str(body.get('TransactionType', '')),
            'first_name': str(body.get('FirstName', '')),
            'middle_name': str(body.get('MiddleName', '')),
            'last_name': str(body.get('LastName', '')),
            'raw_payload': body,
        },
    )
    if not created:
        c2b.raw_payload = body
        c2b.save(update_fields=['raw_payload'])

    logger.info(
        '[c2b_confirmation] TransID=%s amount=%s type=%s msisdn=%s created=%s',
        trans_id, c2b.trans_amount, c2b.transaction_type, c2b.msisdn, created,
    )

    try_activate_c2b_payment(c2b)
    return {'ResultCode': 0, 'ResultDesc': 'Success'}


def verify_receipt_for_payment(payment, receipt_code: str) -> tuple[bool, str]:
    """
    Verify till payment using stored C2B record or wait for callback.
    Returns (activated, message).
    """
    from subscriptions.models import Payment

    code = ''.join(c for c in receipt_code.strip().upper() if c.isalnum())
    c2b = C2bTransaction.objects.filter(trans_id__iexact=code).first()

    if c2b:
        if c2b.trans_amount != payment.amount:
            return False, f'Amount mismatch: you paid KSh {c2b.trans_amount}, plan is KSh {payment.amount}.'
        if Payment.objects.filter(confirmation_code__iexact=code, status='completed').exclude(id=payment.id).exists():
            return False, 'This M-Pesa code was already used for another subscription.'
        c2b.payment = payment
        c2b.save(update_fields=['payment'])
        if activate_subscription_payment(payment, receipt_id=code):
            return True, 'Payment verified and subscription activated.'
        return False, 'Could not activate subscription.'

    # Save code; C2B may arrive shortly
    payment.confirmation_code = code
    payment.transaction_reference = code
    payment.save(update_fields=['confirmation_code', 'transaction_reference', 'updated_at'])
    return False, 'pending'
