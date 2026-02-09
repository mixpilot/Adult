"""
Payment System Verification Script
Run this to check if the monetization system is properly configured.
"""
import os
import sys
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from subscriptions.models import SubscriptionPlan, Subscription, Payment
import stripe

print("=" * 60)
print("PAYMENT SYSTEM VERIFICATION")
print("=" * 60)

# 1. Check Stripe Installation
print("\n1. STRIPE PACKAGE:")
try:
    import stripe
    print(f"   ✅ Stripe installed: {stripe.__version__ if hasattr(stripe, '__version__') else 'Yes'}")
except ImportError:
    print("   ❌ Stripe package not installed")
    print("   Run: pip install stripe")

# 2. Check Stripe Configuration
print("\n2. STRIPE CONFIGURATION:")
stripe_configured = True

if hasattr(settings, 'STRIPE_SECRET_KEY'):
    secret_key = settings.STRIPE_SECRET_KEY
    if secret_key and secret_key != 'sk_test_your_secret_key_here':
        print(f"   ✅ Secret Key: Configured ({secret_key[:20]}...)")
    else:
        print("   ⚠️  Secret Key: NOT CONFIGURED (using placeholder)")
        print("   → Set STRIPE_SECRET_KEY in settings.py or environment")
        stripe_configured = False
else:
    print("   ❌ STRIPE_SECRET_KEY not found in settings")
    stripe_configured = False

if hasattr(settings, 'STRIPE_PUBLISHABLE_KEY'):
    pub_key = settings.STRIPE_PUBLISHABLE_KEY
    if pub_key and pub_key != 'pk_test_your_publishable_key_here':
        print(f"   ✅ Publishable Key: Configured ({pub_key[:20]}...)")
    else:
        print("   ⚠️  Publishable Key: NOT CONFIGURED (using placeholder)")
        stripe_configured = False

if hasattr(settings, 'STRIPE_WEBHOOK_SECRET'):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    if webhook_secret and webhook_secret != 'whsec_your_webhook_secret_here':
        print(f"   ✅ Webhook Secret: Configured")
    else:
        print("   ⚠️  Webhook Secret: NOT CONFIGURED")
        print("   → Set up webhook in Stripe Dashboard and add secret")

# 3. Check Database Models
print("\n3. DATABASE MODELS:")
try:
    plan_count = SubscriptionPlan.objects.count()
    print(f"   ✅ SubscriptionPlan model: {plan_count} plans created")
    
    if plan_count == 0:
        print("   ⚠️  No subscription plans found!")
        print("   → Create plans via Django admin or shell")
    
    sub_count = Subscription.objects.count()
    print(f"   ✅ Subscription model: {sub_count} subscriptions")
    
    payment_count = Payment.objects.count()
    print(f"   ✅ Payment model: {payment_count} payments")
    
except Exception as e:
    print(f"   ❌ Error accessing models: {e}")

# 4. Check Subscription Plans
print("\n4. SUBSCRIPTION PLANS:")
try:
    plans = SubscriptionPlan.objects.filter(is_active=True)
    if plans.exists():
        for plan in plans:
            print(f"   ✅ {plan.name} (${plan.price_monthly}/month)")
            if not plan.stripe_price_id_monthly:
                print(f"      ⚠️  Missing Stripe Price ID for monthly billing")
    else:
        print("   ⚠️  No active subscription plans found")
        print("   → Create plans in Django admin at /admin/subscriptions/subscriptionplan/")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Check URLs
print("\n5. URL ROUTING:")
try:
    from django.urls import reverse
    test_urls = [
        'subscriptions:plans',
        'subscriptions:subscribe',
        'subscriptions:manage',
        'subscriptions:tokens',
    ]
    for url_name in test_urls:
        try:
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
        except:
            print(f"   ❌ {url_name}: Not found")
except Exception as e:
    print(f"   ❌ Error checking URLs: {e}")

# 6. Check Templates
print("\n6. TEMPLATES:")
import os
from pathlib import Path
template_dir = Path('templates/subscriptions')
templates = ['plans.html', 'manage.html', 'tokens.html', 'purchase_tokens.html']
for template in templates:
    template_path = template_dir / template
    if template_path.exists():
        print(f"   ✅ {template}")
    else:
        print(f"   ❌ {template} - Missing")

# 7. Test Stripe Connection
print("\n7. STRIPE API CONNECTION:")
if stripe_configured and settings.STRIPE_SECRET_KEY != 'sk_test_your_secret_key_here':
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Try to retrieve account info (lightweight test)
        account = stripe.Account.retrieve()
        print(f"   ✅ Stripe connection successful")
        print(f"   → Account: {account.get('email', 'N/A')}")
    except stripe.error.AuthenticationError:
        print("   ❌ Invalid Stripe API key")
    except Exception as e:
        print(f"   ⚠️  Stripe connection test failed: {e}")
else:
    print("   ⚠️  Cannot test - Stripe keys not configured")

# 8. Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

issues = []
if not stripe_configured:
    issues.append("Stripe API keys need to be configured")
if SubscriptionPlan.objects.count() == 0:
    issues.append("No subscription plans created")
if not all(Path(f'templates/subscriptions/{t}').exists() for t in templates):
    issues.append("Some templates are missing")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\n📋 TO MAKE IT WORK:")
    print("   1. Get Stripe API keys from https://stripe.com")
    print("   2. Add keys to config/settings.py or environment variables")
    print("   3. Create subscription plans in Django admin")
    print("   4. Create products/prices in Stripe Dashboard")
    print("   5. Add Stripe Price IDs to subscription plans")
    print("   6. Set up webhook endpoint in Stripe Dashboard")
else:
    print("\n✅ SYSTEM READY!")
    print("   All components are configured and ready to use.")

print("\n" + "=" * 60)
