from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plan tiers."""
    TIER_CHOICES = [
        ('free', 'Free'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
        ('once', 'One Time Access'),
    ]
    
    USER_TYPE_CHOICES = [
        ('client', 'Client - For Users Looking for Escorts'),
        ('escort', 'Escort - For Escorts Providing Services'),
        ('both', 'Both - Available for Clients and Escorts'),
    ]
    
    name = models.CharField(max_length=50)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client', help_text="Who is this plan for?")
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_quarterly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_quarterly = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True, null=True)
    
    # Client Features
    unlimited_messaging = models.BooleanField(default=False, help_text="Unlimited messages to escorts")
    unlimited_content_access = models.BooleanField(default=False, help_text="Access to all premium content")
    ad_free = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_search = models.BooleanField(default=False, help_text="Advanced search filters")
    
    # Escort Features
    featured_listing = models.BooleanField(default=False, help_text="Featured placement in search results")
    profile_verification_badge = models.BooleanField(default=False, help_text="Verified escort badge")
    unlimited_photos = models.BooleanField(default=False, help_text="Unlimited profile photos")
    priority_ranking = models.BooleanField(default=False, help_text="Higher ranking in search results")
    earnings_tracking = models.BooleanField(default=False, help_text="Detailed earnings dashboard")
    creator_earnings = models.BooleanField(default=False, help_text="Earn from content and tips")
    max_upload_size = models.IntegerField(default=100, help_text="Max upload size in MB")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price_monthly']
        unique_together = [['tier', 'user_type']]

    def __str__(self):
        from .billing import period_label_for_tier
        label = period_label_for_tier(self.tier)
        suffix = f'/{label.lstrip("/")}' if label.startswith('/') else f' ({label})'
        return f"{self.name} - KSh {self.price_monthly}{suffix}"

    @property
    def default_billing_period(self):
        from .billing import default_billing_for_tier
        return default_billing_for_tier(self.tier)

    @property
    def period_label(self):
        from .billing import period_label_for_tier
        return period_label_for_tier(self.tier)

    def get_price(self, billing_period=None):
        """Get price for this plan (each plan has a single fixed price)."""
        period = billing_period or self.default_billing_period
        if period == 'once' or self.tier == 'once':
            return self.price_monthly
        if period == 'quarterly' and self.price_quarterly:
            return self.price_quarterly
        if period == 'yearly' and self.price_yearly:
            return self.price_yearly
        return self.price_monthly

    @property
    def is_one_time_plan(self):
        return self.tier == 'once'

    @property
    def is_fixed_period_plan(self):
        """Plan duration is tied to tier (daily/weekly/monthly) — no period picker."""
        return self.tier in ('daily', 'weekly', 'premium', 'once')


class Subscription(models.Model):
    """User subscription."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
        ('expired', 'Expired'),
    ]
    
    BILLING_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('once', 'One Time'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES, default='monthly')
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Dates
    start_date = models.DateTimeField(auto_now_add=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active."""
        if self.status == 'active' or self.status == 'trialing':
            if self.current_period_end > timezone.now():
                return True
        return False
    
    @property
    def is_trialing(self):
        """Check if subscription is in trial period."""
        if self.trial_end and self.trial_end > timezone.now():
            return True
        return False
    
    def cancel(self):
        """Cancel subscription."""
        self.status = 'canceled'
        self.canceled_at = timezone.now()
        self.auto_renew = False
        self.save()


class Payment(models.Model):
    """Payment records."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa STK Push'),
        ('mpesa_till', 'M-Pesa Till'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='mobile_money')
    
    # Mobile Payment Fields
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number used for payment")
    transaction_reference = models.CharField(max_length=100, blank=True, null=True, help_text="Mobile money transaction reference")
    confirmation_code = models.CharField(max_length=50, blank=True, null=True, help_text="Payment confirmation code from user")
    
    # Stripe (optional, for future use)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    
    billing_period = models.CharField(max_length=20, default='monthly')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - KSh {self.amount} - {self.status}"


class PromoCode(models.Model):
    """Promotional codes for discounts."""
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Discount
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ], default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.IntegerField(null=True, blank=True, help_text="Maximum number of times this code can be used")
    used_count = models.IntegerField(default=0)
    
    # Restrictions
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True, help_text="Leave empty for all plans")
    first_time_only = models.BooleanField(default=False, help_text="Only for first-time subscribers")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}%"
    
    def is_valid(self, user=None, plan=None):
        """Check if promo code is valid."""
        if not self.is_active:
            return False, "Promo code is not active"
        
        now = timezone.now()
        if now < self.valid_from or now > self.valid_until:
            return False, "Promo code is expired"
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Promo code has reached maximum uses"
        
        if self.applicable_plans.exists() and plan:
            if plan not in self.applicable_plans.all():
                return False, "Promo code not applicable to this plan"
        
        if self.first_time_only and user:
            if Subscription.objects.filter(user=user).exists():
                return False, "Promo code only for first-time subscribers"
        
        return True, "Valid"
    
    def calculate_discount(self, amount):
        """Calculate discount amount."""
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:
            return min(self.discount_value, amount)


class Token(models.Model):
    """Virtual currency/tokens system."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='token_balance')
    balance = models.IntegerField(default=0)
    lifetime_earned = models.IntegerField(default=0)
    lifetime_spent = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.balance} tokens"
    
    def add_tokens(self, amount, reason=''):
        """Add tokens to balance."""
        self.balance += amount
        self.lifetime_earned += amount
        self.save()
        TokenTransaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='earned',
            reason=reason
        )
    
    def spend_tokens(self, amount, reason=''):
        """Spend tokens from balance."""
        if self.balance >= amount:
            self.balance -= amount
            self.lifetime_spent += amount
            self.save()
            TokenTransaction.objects.create(
                user=self.user,
                amount=-amount,
                transaction_type='spent',
                reason=reason
            )
            return True
        return False


class TokenTransaction(models.Model):
    """Token transaction history."""
    TRANSACTION_TYPE_CHOICES = [
        ('purchased', 'Purchased'),
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    reason = models.CharField(max_length=200, blank=True)
    related_content = models.ForeignKey('content.Content', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} tokens - {self.transaction_type}"


class CreatorEarning(models.Model):
    """Creator revenue tracking."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('paid', 'Paid'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    content = models.ForeignKey('content.Content', on_delete=models.CASCADE, related_name='earnings', null=True, blank=True)
    
    # Earning details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    revenue_type = models.CharField(max_length=50, choices=[
        ('subscription', 'Subscription Revenue Share'),
        ('pay_per_view', 'Pay Per View'),
        ('tip', 'Tip'),
        ('premium_access', 'Premium Content Access'),
    ])
    
    # Payout
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout_date = models.DateTimeField(null=True, blank=True)
    payout_method = models.CharField(max_length=50, blank=True)
    
    # Platform fee (typically 30%)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    platform_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    creator_share = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.creator.username} - KSh {self.creator_share} - {self.status}"
    
    def calculate_earnings(self):
        """Calculate creator share after platform fee."""
        self.platform_fee_amount = self.amount * (self.platform_fee_percentage / 100)
        self.creator_share = self.amount - self.platform_fee_amount
        self.save()


class PayPerViewPurchase(models.Model):
    """Pay-per-view content purchases."""
    PAYMENT_METHOD_CHOICES = [
        ('tokens', 'Tokens'),
        ('paystack', 'Paystack'),
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('mtn_mobile_money', 'MTN Mobile Money'),
        ('tigo_pesa', 'Tigo Pesa'),
        ('orange_money', 'Orange Money'),
        ('mobile_money', 'Mobile Money'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ppv_purchases')
    content = models.ForeignKey('content.Content', on_delete=models.CASCADE, related_name='ppv_purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='mobile_money')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.content.title}"


class Tip(models.Model):
    """Tips to creators."""
    PAYMENT_METHOD_CHOICES = [
        ('tokens', 'Tokens'),
        ('paystack', 'Paystack'),
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('mtn_mobile_money', 'MTN Mobile Money'),
        ('tigo_pesa', 'Tigo Pesa'),
        ('orange_money', 'Orange Money'),
        ('mobile_money', 'Mobile Money'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_tips')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_tips')
    content = models.ForeignKey('content.Content', on_delete=models.SET_NULL, null=True, blank=True, related_name='tips')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='mobile_money')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} tipped KSh {self.amount} to {self.to_user.username}"
