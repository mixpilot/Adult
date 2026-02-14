"""
M-Pesa STK Push (prompt) transactions only.
This app handles only M-Pesa prompts; other payment methods stay in subscriptions.
"""
from django.db import models


class MpesaTransaction(models.Model):
    """Records an M-Pesa STK Push (prompt) request and its callback result."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # From our init request
    account_reference = models.CharField(
        max_length=64,
        db_index=True,
        help_text='Our reference, e.g. sub_<payment_id> for subscription payment',
    )
    transaction_desc = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')

    # From Daraja response
    checkout_request_id = models.CharField(max_length=100, unique=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)

    # From Daraja callback
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_description = models.CharField(max_length=512, blank=True)
    callback_metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'M-Pesa transaction'
        verbose_name_plural = 'M-Pesa transactions'

    def __str__(self):
        return f"{self.account_reference} KSh {self.amount} ({self.status})"
