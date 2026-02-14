"""
M-Pesa Daraja API – STK Push (Lipa Na M-Pesa Online) only.
Handles authentication and initiating the payment prompt on the user's phone.
"""
import base64
import json
import logging
import time
from datetime import datetime
from decimal import Decimal
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from django.conf import settings

logger = logging.getLogger(__name__)

# Daraja sandbox allows ~5 requests per 60s. Cache token to avoid OAuth on every status poll.
_mpesa_token_cache = {'token': None, 'expires_at': 0}
_TOKEN_CACHE_SECONDS = 50 * 60  # 50 minutes (tokens expire in ~1h)
_DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; DarajaClient/1.0)'}


class MpesaServiceError(Exception):
    """Raised when M-Pesa API call fails."""
    pass


class MpesaService:
    """Service for M-Pesa STK Push (prompt) via Safaricom Daraja API."""

    def __init__(self):
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.env = getattr(settings, 'MPESA_ENV', 'sandbox').lower()
        self._base_url = (
            'https://sandbox.safaricom.co.ke'
            if self.env == 'sandbox'
            else 'https://api.safaricom.co.ke'
        )

    def _get_access_token(self) -> str:
        """OAuth: get access token from Daraja. Uses in-memory cache to stay under rate limit."""
        global _mpesa_token_cache
        now = time.time()
        if _mpesa_token_cache['token'] and _mpesa_token_cache['expires_at'] > now:
            return _mpesa_token_cache['token']
        url = f'{self._base_url}/oauth/v1/generate?grant_type=client_credentials'
        credentials = base64.b64encode(
            f'{self.consumer_key}:{self.consumer_secret}'.encode()
        ).decode()
        headers = {'Authorization': f'Basic {credentials}', **_DEFAULT_HEADERS}
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                token = data['access_token']
                _mpesa_token_cache = {'token': token, 'expires_at': now + _TOKEN_CACHE_SECONDS}
                return token
        except (HTTPError, URLError, KeyError) as e:
            logger.exception('M-Pesa OAuth failed: %s', e)
            raise MpesaServiceError('Could not get M-Pesa access token') from e

    def _stk_push_password(self) -> str:
        """Lipa Na M-Pesa password: Base64(Shortcode + Passkey + Timestamp)."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        raw = f'{self.shortcode}{self.passkey}{timestamp}'
        return base64.b64encode(raw.encode()).decode()

    def _stk_push_timestamp(self) -> str:
        """Format: YYYYMMDDHHmmss."""
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def normalize_phone(self, phone: str) -> str:
        """Ensure phone is 254XXXXXXXXX for Kenya."""
        p = ''.join(c for c in phone if c.isdigit())
        if p.startswith('0'):
            p = '254' + p[1:]
        elif p.startswith('254'):
            pass
        else:
            p = '254' + p
        return p[:12]

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: Decimal,
        account_reference: str,
        transaction_desc: str,
    ) -> dict:
        """
        Initiate M-Pesa STK Push (prompt). User will see prompt on phone.

        Returns:
            dict with keys: success (bool), checkout_request_id (str), merchant_request_id (str),
            error_message (str if success is False).
        """
        logger.info('[mpesa] initiate_stk_push phone=%s amount=%s account_ref=%s', phone_number, amount, account_reference)

        if not all([self.consumer_key, self.consumer_secret, self.shortcode, self.passkey]):
            logger.warning('[mpesa] STK aborted: missing credentials (key=%s secret=%s shortcode=%s passkey=%s)',
                           bool(self.consumer_key), bool(self.consumer_secret), bool(self.shortcode), bool(self.passkey))
            return {
                'success': False,
                'checkout_request_id': '',
                'merchant_request_id': '',
                'error_message': 'M-Pesa is not configured (missing credentials).',
            }

        phone = self.normalize_phone(phone_number)
        amount_int = int(amount)  # Daraja expects whole shillings
        logger.info('[mpesa] normalized phone=%s amount_int=%s', phone, amount_int)

        base = getattr(settings, 'MPESA_CALLBACK_BASE_URL', '').rstrip('/')
        callback_url = getattr(settings, 'MPESA_CALLBACK_URL', None) or (f'{base}/payments/mpesa/callback/' if base else '')
        logger.info('[mpesa] callback_url=%s', callback_url or '(empty)')

        try:
            token = self._get_access_token()
            logger.info('[mpesa] OAuth token obtained')
        except MpesaServiceError as e:
            logger.warning('[mpesa] OAuth failed: %s', e)
            return {
                'success': False,
                'checkout_request_id': '',
                'merchant_request_id': '',
                'error_message': str(e),
            }

        url = f'{self._base_url}/mpesa/stkpush/v1/processrequest'
        logger.info('[mpesa] POST %s', url)
        timestamp = self._stk_push_timestamp()
        password = self._stk_push_password()

        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount_int,
            'PartyA': phone,
            'PartyB': self.shortcode,
            'PhoneNumber': phone,
            'CallBackURL': callback_url,
            'AccountReference': account_reference[:12],
            'TransactionDesc': transaction_desc[:13],
        }

        req = Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
                **_DEFAULT_HEADERS,
            },
            method='POST',
        )
        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                rid = data.get('CheckoutRequestID', '')
                mid = data.get('MerchantRequestID', '')
                err_msg = data.get('errorMessage', '')
                logger.info('[mpesa] STK response CheckoutRequestID=%s MerchantRequestID=%s errorMessage=%s', rid, mid, err_msg)
                if rid:
                    logger.info('[mpesa] STK success')
                    return {
                        'success': True,
                        'checkout_request_id': rid,
                        'merchant_request_id': mid,
                        'error_message': '',
                    }
                logger.warning('[mpesa] STK API returned error: %s', err_msg or 'Unknown')
                return {
                    'success': False,
                    'checkout_request_id': '',
                    'merchant_request_id': '',
                    'error_message': err_msg or 'Unknown M-Pesa error',
                }
        except HTTPError as e:
            body = e.read().decode() if e.fp else ''
            try:
                err = json.loads(body)
                msg = err.get('errorMessage', body or str(e))
            except Exception:
                msg = body or str(e)
            logger.exception('M-Pesa STK Push HTTP error: %s', msg)
            return {
                'success': False,
                'checkout_request_id': '',
                'merchant_request_id': '',
                'error_message': msg,
            }
        except (URLError, json.JSONDecodeError) as e:
            logger.exception('M-Pesa STK Push failed: %s', e)
            return {
                'success': False,
                'checkout_request_id': '',
                'merchant_request_id': '',
                'error_message': str(e),
            }

    def query_stk_push(self, checkout_request_id: str) -> dict:
        """
        Query Lipa Na M-Pesa Online transaction status by CheckoutRequestID.
        Use this when you don't have a callback URL – poll until ResultCode is 0 (success) or failed.
        Daraja expects BusinessShortCode, Password, Timestamp and CheckoutRequestID.

        Returns:
            dict with: success (bool), result_code (int), result_desc (str),
            mpesa_receipt_number (str), amount (optional), error_message (str).
            On API errors (400/403/429): result_code -1, error_message set; rate_limit=True for 429.
        """
        if not checkout_request_id:
            return {
                'success': False,
                'result_code': -1,
                'result_desc': 'Missing CheckoutRequestID',
                'mpesa_receipt_number': '',
                'error_message': 'Missing CheckoutRequestID',
                'rate_limit': False,
            }
        if not all([self.consumer_key, self.consumer_secret, self.shortcode, self.passkey]):
            return {
                'success': False,
                'result_code': -1,
                'result_desc': 'M-Pesa not configured',
                'mpesa_receipt_number': '',
                'error_message': 'M-Pesa is not configured (missing credentials).',
                'rate_limit': False,
            }
        try:
            token = self._get_access_token()
        except MpesaServiceError as e:
            return {
                'success': False,
                'result_code': -1,
                'result_desc': str(e),
                'mpesa_receipt_number': '',
                'error_message': str(e),
                'rate_limit': False,
            }
        url = f'{self._base_url}/mpesa/stkpushquery/v1/query'
        timestamp = self._stk_push_timestamp()
        password = self._stk_push_password()
        # Daraja STK Query requires same auth as STK Push: shortcode, password, timestamp
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id,
        }
        req = Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
                **_DEFAULT_HEADERS,
            },
            method='POST',
        )
        logger.warning('[mpesa] STK query request checkout_request_id=%s', (checkout_request_id or '')[:24])
        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
                data = json.loads(raw)
                logger.warning('[mpesa] STK query 200 raw_keys=%s ResultCode=%s ResultDesc=%s',
                               list(data.keys()), data.get('ResultCode'), data.get('ResultDesc'))
        except HTTPError as e:
            body = e.read().decode() if e.fp else ''
            try:
                err_body = json.loads(body) if body else {}
                err_msg = err_body.get('errorMessage', err_body.get('error', body or str(e)))
            except Exception:
                err_msg = body or str(e)
            logger.warning('M-Pesa STK query HTTP %s: %s', e.code, err_msg)
            return {
                'success': False,
                'result_code': -1,
                'result_desc': err_msg,
                'mpesa_receipt_number': '',
                'error_message': err_msg,
                'rate_limit': e.code == 429,
            }
        except (URLError, json.JSONDecodeError) as e:
            logger.exception('M-Pesa STK query failed: %s', e)
            return {
                'success': False,
                'result_code': -1,
                'result_desc': str(e),
                'mpesa_receipt_number': '',
                'error_message': str(e),
                'rate_limit': False,
            }
        rc = data.get('ResultCode', -1)
        try:
            result_code = int(rc) if rc not in (None, '') else -1
        except (TypeError, ValueError):
            result_code = -1
        result_desc = data.get('ResultDesc', '') or ''
        # ResultCode 0 = success; 1032 = cancelled by user; 1037 = timeout; 1 = other failure
        receipt_number = ''
        amount = None
        params = data.get('ResultParameters') or data.get('ResultParams') or {}
        param_list = params.get('Parameter') or params.get('Item') or []
        for p in param_list:
            if isinstance(p, dict):
                key = (p.get('Key') or p.get('Name') or '').strip()
                val = p.get('Value')
                if key == 'MpesaReceiptNumber':
                    receipt_number = str(val or '')
                if key == 'Amount':
                    amount = val
        if result_code == 0:
            return {
                'success': True,
                'result_code': result_code,
                'result_desc': result_desc,
                'mpesa_receipt_number': receipt_number,
                'amount': amount,
                'error_message': '',
                'rate_limit': False,
            }
        return {
            'success': False,
            'result_code': result_code,
            'result_desc': result_desc,
            'mpesa_receipt_number': '',
            'amount': amount,
            'error_message': result_desc or f'ResultCode {result_code}',
            'rate_limit': False,
        }
