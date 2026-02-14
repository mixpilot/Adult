from django.contrib import admin
from .models import MpesaTransaction


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'account_reference', 'phone_number', 'amount', 'status',
        'mpesa_receipt_number', 'result_code', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('account_reference', 'phone_number', 'mpesa_receipt_number', 'checkout_request_id')
    readonly_fields = (
        'checkout_request_id', 'merchant_request_id', 'result_code', 'result_description',
        'callback_metadata', 'created_at', 'updated_at',
    )
