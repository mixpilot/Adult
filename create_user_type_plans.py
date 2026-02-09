"""
Script to create subscription plans for clients and escorts
Run: python create_user_type_plans.py
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

print("Creating subscription plans for clients and escorts...")

# Helper function to get or create plan
def get_or_create_plan(**kwargs):
    tier = kwargs.get('tier')
    user_type = kwargs.get('user_type')
    plan, created = SubscriptionPlan.objects.get_or_create(
        tier=tier,
        user_type=user_type,
        defaults=kwargs
    )
    if not created:
        # Update existing plan
        for key, value in kwargs.items():
            setattr(plan, key, value)
        plan.save()
        return plan, False
    return plan, True

# Show existing plans
existing = SubscriptionPlan.objects.filter(user_type__in=['client', 'escort']).count()
if existing > 0:
    print(f"[!] {existing} plans already exist. Will update/create missing ones.")
    print("Existing plans:")
    for plan in SubscriptionPlan.objects.filter(user_type__in=['client', 'escort']):
        print(f"  - {plan.name} ({plan.user_type}) - KSh {plan.price_monthly}/month")

print("\n" + "="*60)
# CLIENT PLANS
print("\n[CLIENT] Creating/updating CLIENT plans...")

# Free Client Plan
free_client, created = get_or_create_plan(
    name='Free',
    tier='free',
    user_type='client',
    description='Basic access for clients. Browse escorts and send limited messages.',
    price_monthly=0,
    unlimited_messaging=False,
    unlimited_content_access=False,
    advanced_search=False,
    ad_free=False,
    priority_support=False,
    max_upload_size=100,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {free_client.name} (Client)")

# Basic Client Plan
basic_client, created = get_or_create_plan(
    name='Basic',
    tier='basic',
    user_type='client',
    description='Enhanced features for clients. Unlimited messaging and basic search.',
    price_monthly=1299.00,  # KSh 1,299
    price_quarterly=3506.00,  # KSh 3,506 (10% discount)
    price_yearly=12467.00,  # KSh 12,467 (20% discount)
    unlimited_messaging=True,
    unlimited_content_access=False,
    advanced_search=False,
    ad_free=False,
    priority_support=False,
    max_upload_size=200,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {basic_client.name} (Client)")

# Premium Client Plan
premium_client, created = get_or_create_plan(
    name='Premium',
    tier='premium',
    user_type='client',
    description='Full access for clients. Unlimited messaging, content, and advanced search.',
    price_monthly=2599.00,  # KSh 2,599
    price_quarterly=7016.00,  # KSh 7,016 (10% discount)
    price_yearly=24947.00,  # KSh 24,947 (20% discount)
    unlimited_messaging=True,
    unlimited_content_access=True,
    ad_free=True,
    advanced_search=True,
    priority_support=False,
    max_upload_size=500,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {premium_client.name} (Client)")

# VIP Client Plan
vip_client, created = get_or_create_plan(
    name='VIP',
    tier='vip',
    user_type='client',
    description='Ultimate client experience. All premium features plus priority support.',
    price_monthly=5199.00,  # KSh 5,199
    price_quarterly=14036.00,  # KSh 14,036 (10% discount)
    price_yearly=49907.00,  # KSh 49,907 (20% discount)
    unlimited_messaging=True,
    unlimited_content_access=True,
    ad_free=True,
    advanced_search=True,
    priority_support=True,
    max_upload_size=1000,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {vip_client.name} (Client)")

# ESCORT PLANS
print("\n[ESCORT] Creating/updating ESCORT plans...")

# Free Escort Plan
free_escort, created = get_or_create_plan(
    name='Free',
    tier='free',
    user_type='escort',
    description='Basic listing for escorts. Create profile and receive messages.',
    price_monthly=0,
    featured_listing=False,
    profile_verification_badge=False,
    unlimited_photos=False,
    priority_ranking=False,
    earnings_tracking=False,
    creator_earnings=False,
    priority_support=False,
    max_upload_size=100,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {free_escort.name} (Escort)")

# Basic Escort Plan
basic_escort, created = get_or_create_plan(
    name='Basic',
    tier='basic',
    user_type='escort',
    description='Enhanced features for escorts. More photos and basic earnings tracking.',
    price_monthly=1949.00,  # KSh 1,949
    price_quarterly=5261.00,  # KSh 5,261 (10% discount)
    price_yearly=18707.00,  # KSh 18,707 (20% discount)
    unlimited_photos=True,
    earnings_tracking=True,
    featured_listing=False,
    priority_ranking=False,
    profile_verification_badge=False,
    creator_earnings=False,
    priority_support=False,
    max_upload_size=200,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {basic_escort.name} (Escort)")

# Premium Escort Plan
premium_escort, created = get_or_create_plan(
    name='Premium',
    tier='premium',
    user_type='escort',
    description='Full features for escorts. Featured listing, verified badge, and priority ranking.',
    price_monthly=3899.00,  # KSh 3,899
    price_quarterly=10526.00,  # KSh 10,526 (10% discount)
    price_yearly=37427.00,  # KSh 37,427 (20% discount)
    featured_listing=True,
    profile_verification_badge=True,
    unlimited_photos=True,
    priority_ranking=True,
    earnings_tracking=True,
    creator_earnings=True,
    priority_support=False,
    max_upload_size=500,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {premium_escort.name} (Escort)")

# VIP Escort Plan
vip_escort, created = get_or_create_plan(
    name='VIP',
    tier='vip',
    user_type='escort',
    description='Ultimate escort experience. Top placement, verified badge, and maximum earnings.',
    price_monthly=6499.00,  # KSh 6,499
    price_quarterly=17546.00,  # KSh 17,546 (10% discount)
    price_yearly=62387.00,  # KSh 62,387 (20% discount)
    featured_listing=True,
    profile_verification_badge=True,
    unlimited_photos=True,
    priority_ranking=True,
    earnings_tracking=True,
    creator_earnings=True,
    priority_support=True,
    max_upload_size=1000,
)
print(f"{'[+] Created' if created else '[~] Updated'}: {vip_escort.name} (Escort)")

print("\n" + "="*60)
print("[OK] All subscription plans created/updated!")
print("="*60)

# Summary
client_count = SubscriptionPlan.objects.filter(user_type='client').count()
escort_count = SubscriptionPlan.objects.filter(user_type='escort').count()

print("\n[SUMMARY]")
print(f"  - Client Plans: {client_count} (Free, Basic, Premium, VIP)")
print(f"  - Escort Plans: {escort_count} (Free, Basic, Premium, VIP)")
print("\n[INFO] Users can now subscribe based on their account type!")
print("\n[PRICING] All prices are in Kenyan Shillings (KES)")
print("  Client: Free (0), Basic (1,299), Premium (2,599), VIP (5,199)")
print("  Escort: Free (0), Basic (1,949), Premium (3,899), VIP (6,499)")
