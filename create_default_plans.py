"""
Script to create default subscription plans
Run: python manage.py shell < create_default_plans.py
Or: python create_default_plans.py
"""
import os
import sys
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from subscriptions.models import SubscriptionPlan

print("Creating default subscription plans...")

# Check if plans already exist
if SubscriptionPlan.objects.exists():
    print("⚠️  Plans already exist. Skipping creation.")
    print("Existing plans:")
    for plan in SubscriptionPlan.objects.all():
        print(f"  - {plan.name} (${plan.price_monthly}/month)")
else:
    # Create Free plan
    free = SubscriptionPlan.objects.create(
        name='Free',
        tier='free',
        description='Basic access with limited features. Perfect for getting started.',
        price_monthly=0,
        unlimited_messaging=False,
        unlimited_content_access=False,
        ad_free=False,
        advanced_search=False,
    )
    print(f"✅ Created: {free.name}")

    # Create Basic plan
    basic = SubscriptionPlan.objects.create(
        name='Basic',
        tier='basic',
        description='Enhanced features for casual users. Unlimited messaging and basic access.',
        price_monthly=9.99,
        price_quarterly=26.97,  # 10% discount
        price_yearly=95.90,  # 20% discount
        unlimited_messaging=True,
        unlimited_content_access=False,
        ad_free=False,
        advanced_search=False,
    )
    print(f"✅ Created: {basic.name}")

    # Create Premium plan
    premium = SubscriptionPlan.objects.create(
        name='Premium',
        tier='premium',
        description='Full access to all premium features. Unlimited content, ad-free experience, and advanced search.',
        price_monthly=19.99,
        price_quarterly=53.97,
        price_yearly=191.90,
        unlimited_messaging=True,
        unlimited_content_access=True,
        ad_free=True,
        advanced_search=True,
    )
    print(f"✅ Created: {premium.name}")

    # Create VIP plan
    vip = SubscriptionPlan.objects.create(
        name='VIP',
        tier='vip',
        description='Ultimate experience with creator earnings. All premium features plus priority support and creator monetization.',
        price_monthly=39.99,
        price_quarterly=107.97,
        price_yearly=383.90,
        unlimited_messaging=True,
        unlimited_content_access=True,
        ad_free=True,
        advanced_search=True,
        priority_support=True,
        creator_earnings=True,
        max_upload_size=500,
    )
    print(f"✅ Created: {vip.name}")

    print("\n" + "="*60)
    print("✅ All subscription plans created!")
    print("="*60)
    print("\n⚠️  IMPORTANT NEXT STEPS:")
    print("1. Go to Stripe Dashboard → Products")
    print("2. Create products for each plan (Free, Basic, Premium, VIP)")
    print("3. Create prices for monthly, quarterly, yearly billing")
    print("4. Copy the Price IDs (they look like 'price_xxxxx')")
    print("5. Go to Django admin → Subscriptions → Subscription Plans")
    print("6. Edit each plan and add the Stripe Price IDs")
    print("\n💡 Test card: 4242 4242 4242 4242 (any future expiry, any CVC)")
