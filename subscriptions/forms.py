from django import forms
from django.db import models
from .models import SubscriptionPlan, PromoCode


class SubscriptionForm(forms.Form):
    """Form for selecting subscription plan."""
    def __init__(self, *args, user_type='client', **kwargs):
        super().__init__(*args, **kwargs)
        # Filter plans by user type
        self.fields['plan'].queryset = SubscriptionPlan.objects.filter(
            is_active=True
        ).filter(
            models.Q(user_type=user_type) | models.Q(user_type='both')
        ).order_by('price_monthly')
    
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None
    )
    billing_period = forms.ChoiceField(
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly (Save 10%)'),
            ('yearly', 'Yearly (Save 20%)'),
        ],
        widget=forms.RadioSelect,
        initial='monthly'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('paystack', 'Paystack'),
            ('mpesa', 'M-Pesa'),
            ('airtel_money', 'Airtel Money'),
            ('mtn_mobile_money', 'MTN Mobile Money'),
            ('tigo_pesa', 'Tigo Pesa'),
            ('orange_money', 'Orange Money'),
            ('vodacom_mpesa', 'Vodacom M-Pesa'),
            ('mobile_money', 'Other Mobile Money'),
        ],
        widget=forms.RadioSelect,
        initial='paystack',
        label='Payment Method'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0712345678',
            'pattern': '[0-9+\\-\\s()]+'
        }),
        help_text='Enter your mobile money phone number'
    )
    promo_code = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code (optional)'
        })
    )


class PromoCodeForm(forms.Form):
    """Form for applying promo code."""
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code'
        })
    )


class TokenPurchaseForm(forms.Form):
    """Form for purchasing tokens."""
    TOKEN_PACKAGES = [
        (100, '100 Tokens - KSh 1,300.00'),
        (250, '250 Tokens - KSh 3,250.00 (Save KSh 325.00)'),
        (500, '500 Tokens - KSh 6,500.00 (Save KSh 1,300.00)'),
        (1000, '1000 Tokens - KSh 12,000.00 (Save KSh 3,250.00)'),
    ]
    
    token_amount = forms.ChoiceField(
        choices=TOKEN_PACKAGES,
        widget=forms.RadioSelect,
        label='Select Token Package'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('paystack', 'Paystack'),
            ('mpesa', 'M-Pesa'),
            ('airtel_money', 'Airtel Money'),
            ('mtn_mobile_money', 'MTN Mobile Money'),
            ('tigo_pesa', 'Tigo Pesa'),
            ('orange_money', 'Orange Money'),
            ('vodacom_mpesa', 'Vodacom M-Pesa'),
            ('mobile_money', 'Other Mobile Money'),
        ],
        widget=forms.RadioSelect,
        initial='paystack',
        label='Payment Method'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0712345678',
            'pattern': '[0-9+\\-\\s()]+'
        }),
        help_text='Enter your mobile money phone number'
    )


class TipForm(forms.Form):
    """Form for tipping creators."""
    amount = forms.DecimalField(
        min_value=1.00,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    message = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional message...'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('tokens', 'Use Tokens'),
            ('paystack', 'Paystack'),
            ('mpesa', 'M-Pesa'),
            ('airtel_money', 'Airtel Money'),
            ('mtn_mobile_money', 'MTN Mobile Money'),
            ('tigo_pesa', 'Tigo Pesa'),
            ('orange_money', 'Orange Money'),
            ('mobile_money', 'Mobile Money'),
        ],
        initial='mobile_money',
        widget=forms.RadioSelect
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (if using mobile money)'
        })
    )
