"""
Paystack transaction initialization and verification.
"""
import json
import logging
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from django.conf import settings

logger = logging.getLogger(__name__)


class PaystackService:
    """Service for Paystack payments (same API endpoints for test/live)."""

    def __init__(self):
        self.env = getattr(settings, 'PAYSTACK_ENV', 'sandbox').lower()
        self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY_ACTIVE', '') or getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        self.public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY_ACTIVE', '') or getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        self.base_url = getattr(settings, 'PAYSTACK_BASE_URL', 'https://api.paystack.co').rstrip('/')

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; PaystackClient/1.0)',
        }

    @staticmethod
    def _to_subunits(amount: Decimal) -> int:
        """Convert major currency unit to minor subunit used by Paystack."""
        try:
            return int((Decimal(amount) * 100).quantize(Decimal('1')))
        except (InvalidOperation, TypeError, ValueError):
            return 0

    def initialize_transaction(
        self,
        email: str,
        amount: Decimal,
        reference: str,
        callback_url: str,
        metadata: dict | None = None,
        currency: str = 'KES',
    ) -> dict:
        """
        Initialize a hosted checkout transaction.
        Returns dict with keys:
          success, authorization_url, access_code, reference, error_message.
        """
        if not self.secret_key:
            return {
                'success': False,
                'authorization_url': '',
                'access_code': '',
                'reference': reference,
                'error_message': 'Paystack is not configured (missing secret key).',
            }

        payload = {
            'email': (email or '').strip(),
            'amount': self._to_subunits(amount),
            'reference': reference,
            'callback_url': callback_url,
            'currency': (currency or 'KES').upper(),
            'metadata': metadata or {},
        }
        req = Request(
            f'{self.base_url}/transaction/initialize',
            data=json.dumps(payload).encode(),
            headers=self._headers(),
            method='POST',
        )

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode() if e.fp else ''
            try:
                parsed = json.loads(body) if body else {}
                msg = parsed.get('message') or body or str(e)
            except Exception:
                msg = body or str(e)
            logger.warning('[paystack] initialize HTTP %s: %s', getattr(e, 'code', '?'), msg)
            return {
                'success': False,
                'authorization_url': '',
                'access_code': '',
                'reference': reference,
                'error_message': msg,
            }
        except (URLError, json.JSONDecodeError) as e:
            logger.warning('[paystack] initialize failed: %s', e)
            return {
                'success': False,
                'authorization_url': '',
                'access_code': '',
                'reference': reference,
                'error_message': str(e),
            }

        if not data.get('status'):
            return {
                'success': False,
                'authorization_url': '',
                'access_code': '',
                'reference': reference,
                'error_message': data.get('message') or 'Failed to initialize Paystack transaction.',
            }

        tx = data.get('data') or {}
        return {
            'success': bool(tx.get('authorization_url')),
            'authorization_url': tx.get('authorization_url', ''),
            'access_code': tx.get('access_code', ''),
            'reference': tx.get('reference', reference),
            'error_message': '' if tx.get('authorization_url') else 'Missing authorization URL from Paystack.',
        }

    def verify_transaction(self, reference: str) -> dict:
        """
        Verify transaction by reference.
        Returns dict with keys:
          success, paid, status, reference, gateway_response, error_message.
        """
        if not self.secret_key:
            return {
                'success': False,
                'paid': False,
                'status': '',
                'reference': reference,
                'gateway_response': '',
                'error_message': 'Paystack is not configured (missing secret key).',
            }
        if not reference:
            return {
                'success': False,
                'paid': False,
                'status': '',
                'reference': '',
                'gateway_response': '',
                'error_message': 'Missing transaction reference.',
            }

        encoded_ref = quote(reference, safe='')
        req = Request(
            f'{self.base_url}/transaction/verify/{encoded_ref}',
            headers=self._headers(),
            method='GET',
        )

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode() if e.fp else ''
            try:
                parsed = json.loads(body) if body else {}
                msg = parsed.get('message') or body or str(e)
            except Exception:
                msg = body or str(e)
            logger.warning('[paystack] verify HTTP %s: %s', getattr(e, 'code', '?'), msg)
            return {
                'success': False,
                'paid': False,
                'status': '',
                'reference': reference,
                'gateway_response': '',
                'error_message': msg,
            }
        except (URLError, json.JSONDecodeError) as e:
            logger.warning('[paystack] verify failed: %s', e)
            return {
                'success': False,
                'paid': False,
                'status': '',
                'reference': reference,
                'gateway_response': '',
                'error_message': str(e),
            }

        if not data.get('status'):
            return {
                'success': False,
                'paid': False,
                'status': '',
                'reference': reference,
                'gateway_response': '',
                'error_message': data.get('message') or 'Could not verify transaction.',
            }

        tx = data.get('data') or {}
        status = (tx.get('status') or '').lower()
        paid = status == 'success'
        return {
            'success': True,
            'paid': paid,
            'status': status,
            'reference': tx.get('reference', reference),
            'gateway_response': tx.get('gateway_response', ''),
            'error_message': '' if paid else (tx.get('gateway_response') or data.get('message') or 'Payment not completed.'),
        }
