"""
M-Pesa Daraja API Integration
Handles STK Push (Lipa na M-Pesa) and payment callbacks
"""
import requests
import base64
from datetime import datetime
from django.conf import settings
import json


class DarajaAPI:
    """M-Pesa Daraja API client."""
    
    # Sandbox URLs
    SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"
    
    def __init__(self):
        self.consumer_key = getattr(settings, 'DARAJACONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'DARAJACONSUMER_SECRET', '')
        self.shortcode = getattr(settings, 'DARAJASHORTCODE', '174379')  # Test shortcode
        self.passkey = getattr(settings, 'DARAJAPASSKEY', '')  # For production
        self.is_sandbox = getattr(settings, 'DARAJASANDBOX', True)
        self.base_url = self.SANDBOX_BASE_URL if self.is_sandbox else self.PRODUCTION_BASE_URL
        
    def get_access_token(self):
        """
        Get OAuth access token from Daraja API.
        Returns: access_token string or None if failed
        """
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Encode credentials
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
    
    def get_timestamp(self):
        """Get current timestamp in format: YYYYMMDDHHmmss"""
        return datetime.now().strftime('%Y%m%d%H%M%S')
    
    def get_password(self, timestamp):
        """
        Generate password for STK Push.
        Format: base64(Shortcode + Passkey + Timestamp)
        """
        if self.is_sandbox:
            # Sandbox uses test passkey
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        else:
            passkey = self.passkey
            
        password_string = f"{self.shortcode}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc, callback_url):
        """
        Initiate STK Push (Lipa na M-Pesa) payment request.
        
        Args:
            phone_number: Customer phone number (format: 254712345678)
            amount: Amount to charge
            account_reference: Unique reference (e.g., transaction ID)
            transaction_desc: Description of transaction
            callback_url: URL to receive payment confirmation
            
        Returns:
            dict with response data or None if failed
        """
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        timestamp = self.get_timestamp()
        password = self.get_password(timestamp)
        
        # Format phone number (remove + or 0, add 254)
        phone = phone_number.replace('+', '').replace(' ', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            phone = '254' + phone
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error initiating STK Push: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def query_stk_status(self, checkout_request_id):
        """
        Query the status of an STK Push transaction.
        
        Args:
            checkout_request_id: The checkout request ID from STK Push response
            
        Returns:
            dict with transaction status or None if failed
        """
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        timestamp = self.get_timestamp()
        password = self.get_password(timestamp)
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error querying STK status: {e}")
            return None
