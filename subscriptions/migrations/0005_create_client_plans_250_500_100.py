# Data migration: ensure client plans exist - KSh 250/month, KSh 500/month, KSh 100 one-time

from decimal import Decimal
from django.db import migrations


def create_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    # Client plans: Standard 250/mo, Premium 500/mo, One Time 100
    plans_data = [
        {
            'tier': 'basic',
            'user_type': 'client',
            'name': 'Standard',
            'description': 'Access verified escorts, message and connect. Perfect to get started.',
            'price_monthly': Decimal('250.00'),
            'price_quarterly': None,
            'price_yearly': None,
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'ad_free': False,
            'advanced_search': True,
        },
        {
            'tier': 'premium',
            'user_type': 'client',
            'name': 'Premium',
            'description': 'Full access, priority support, and ad-free experience. Best value.',
            'price_monthly': Decimal('500.00'),
            'price_quarterly': Decimal('1350.00'),  # 10% off
            'price_yearly': Decimal('4800.00'),    # 20% off
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'ad_free': True,
            'advanced_search': True,
            'priority_support': True,
        },
        {
            'tier': 'once',
            'user_type': 'client',
            'name': 'One Time Access',
            'description': 'One-time payment for 30 days access. No renewal.',
            'price_monthly': Decimal('100.00'),
            'price_quarterly': None,
            'price_yearly': None,
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'ad_free': False,
            'advanced_search': True,
        },
    ]
    for data in plans_data:
        SubscriptionPlan.objects.update_or_create(
            tier=data['tier'],
            user_type=data['user_type'],
            defaults={
                'name': data['name'],
                'description': data['description'],
                'price_monthly': data['price_monthly'],
                'price_quarterly': data.get('price_quarterly'),
                'price_yearly': data.get('price_yearly'),
                'unlimited_messaging': data.get('unlimited_messaging', False),
                'unlimited_content_access': data.get('unlimited_content_access', False),
                'ad_free': data.get('ad_free', False),
                'advanced_search': data.get('advanced_search', False),
                'priority_support': data.get('priority_support', False),
                'is_active': True,
            },
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_alter_payment_currency'),
    ]

    operations = [
        migrations.RunPython(create_plans, noop),
    ]
