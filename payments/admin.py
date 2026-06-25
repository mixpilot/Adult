from django.contrib import admin
from .models import C2bTransaction, MpesaTransaction


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


@admin.register(C2bTransaction)
class C2bTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'trans_id', 'trans_amount', 'msisdn', 'transaction_type', 'payment', 'created_at',
    )
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('trans_id', 'msisdn', 'bill_ref_number', 'business_shortcode')
    readonly_fields = ('raw_payload', 'created_at')
