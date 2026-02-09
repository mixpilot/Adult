from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    SubscriptionPlan, Subscription, Payment, PromoCode,
    Token, TokenTransaction, CreatorEarning, PayPerViewPurchase, Tip
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ['name', 'tier', 'price_monthly', 'is_active', 'created_at']
    list_filter = ['tier', 'is_active']
    search_fields = ['name', 'tier']
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'tier', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_quarterly', 'price_yearly')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id_monthly', 'stripe_price_id_quarterly', 'stripe_price_id_yearly')
        }),
        ('Features', {
            'fields': (
                'unlimited_messaging', 'unlimited_content_access', 'ad_free',
                'priority_support', 'advanced_search', 'creator_earnings', 'max_upload_size'
            )
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ['user', 'plan', 'status', 'billing_period', 'current_period_end', 'auto_renew']
    list_filter = ['status', 'billing_period', 'plan']
    search_fields = ['user__username', 'user__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'stripe_payment_intent_id', 'stripe_charge_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_until', 'used_count']
    list_filter = ['is_active', 'discount_type', 'first_time_only']
    search_fields = ['code', 'description']
    filter_horizontal = ['applicable_plans']


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    list_display = ['user', 'balance', 'lifetime_earned', 'lifetime_spent']
    search_fields = ['user__username']
    readonly_fields = ['lifetime_earned', 'lifetime_spent', 'updated_at']


@admin.register(TokenTransaction)
class TokenTransactionAdmin(ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(CreatorEarning)
class CreatorEarningAdmin(ModelAdmin):
    list_display = ['creator', 'content', 'amount', 'creator_share', 'status', 'created_at']
    list_filter = ['status', 'revenue_type', 'created_at']
    search_fields = ['creator__username', 'content__title']
    readonly_fields = ['platform_fee_amount', 'creator_share', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(PayPerViewPurchase)
class PayPerViewPurchaseAdmin(ModelAdmin):
    list_display = ['user', 'content', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['user__username', 'content__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Tip)
class TipAdmin(ModelAdmin):
    list_display = ['from_user', 'to_user', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
