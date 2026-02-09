from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model with additional fields."""
    USER_TYPE_CHOICES = [
        ('client', 'Client - Looking for Escorts'),
        ('escort', 'Escort - Providing Services'),
    ]
    
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Mobile phone number for payments")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client', help_text="Are you looking for escorts or providing escort services?")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
    def has_premium_access(self):
        """Check if user has active premium subscription."""
        if hasattr(self, 'subscription'):
            return self.subscription.is_active
        return False
    
    def has_subscription_tier(self, tier):
        """Check if user has specific subscription tier."""
        if hasattr(self, 'subscription'):
            return self.subscription.is_active and self.subscription.plan.tier == tier
        return False
    
    def get_subscription_tier(self):
        """Get user's current subscription tier."""
        if hasattr(self, 'subscription') and self.subscription.is_active:
            return self.subscription.plan.tier
        return 'free'
    
    def can_access_premium_content(self):
        """Check if user can access premium content."""
        return self.has_premium_access() or self.is_staff
    
    def get_token_balance(self):
        """Get user's token balance."""
        from subscriptions.models import Token
        token, created = Token.objects.get_or_create(user=self)
        return token.balance
    
    @property
    def is_escort(self):
        """Check if user is an escort."""
        return self.user_type == 'escort'
    
    @property
    def is_client(self):
        """Check if user is a client."""
        return self.user_type == 'client'
    
    def is_escort_verified(self):
        """Check if escort has minimum required verification (phone + photo)."""
        if not self.is_escort:
            return False
        if not hasattr(self, 'hookup_profile'):
            return False
        profile = self.hookup_profile
        # Escorts need: phone verification AND at least one profile photo
        has_phone_verification = profile.phone_verified
        has_photo = profile.profile_photos.exists()
        return has_phone_verification and has_photo
    
    def is_client_verified(self):
        """Check if client has minimum verification (phone verification)."""
        if not self.is_client:
            return False
        if not hasattr(self, 'hookup_profile'):
            return False
        return self.hookup_profile.phone_verified
    
    def is_id_verified(self):
        """Check if user has ID verification."""
        if not hasattr(self, 'hookup_profile'):
            return False
        return self.hookup_profile.id_verified
    
    def has_any_verification(self):
        """Check if user has any type of verification."""
        if not hasattr(self, 'hookup_profile'):
            return False
        profile = self.hookup_profile
        return profile.is_verified or profile.id_verified or profile.phone_verified
    
    def can_use_premium_features(self):
        """Check if user can use premium features (requires ID verification for premium users)."""
        if not self.has_premium_access():
            return False
        # Premium users must have ID verification
        return self.is_id_verified() or self.is_staff
