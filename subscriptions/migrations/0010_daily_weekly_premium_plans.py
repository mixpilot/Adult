# Pricing update: Daily 150, Weekly 200, Premium monthly 500 (buyers & sellers)

from decimal import Decimal
from django.db import migrations, models


def _upsert_plan(SubscriptionPlan, data):
    """Create or update one plan per tier; prod may have duplicate rows from old migrations."""
    tier = data['tier']
    user_type = data['user_type']
    field_defaults = {
        k: v for k, v in data.items() if k not in ('tier', 'user_type')
    }

    # Retire legacy tiers (client/escort copies of premium, standard, etc.)
    SubscriptionPlan.objects.filter(tier=tier).exclude(user_type=user_type).update(is_active=False)

    matches = list(
        SubscriptionPlan.objects.filter(tier=tier, user_type=user_type).order_by('id')
    )
    if len(matches) > 1:
        plan = matches[0]
        SubscriptionPlan.objects.filter(
            id__in=[p.id for p in matches[1:]],
        ).update(is_active=False)
    elif matches:
        plan = matches[0]
    else:
        plan = SubscriptionPlan(tier=tier, user_type=user_type)

    for key, value in field_defaults.items():
        setattr(plan, key, value)
    plan.is_active = True
    plan.save()


def update_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')

    SubscriptionPlan.objects.filter(tier__in=('basic', 'once')).update(is_active=False)

    plans_data = [
        {
            'tier': 'daily',
            'user_type': 'both',
            'name': 'Daily',
            'price_monthly': Decimal('150.00'),
            'description': 'Full access for 24 hours. For clients and escorts.',
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'advanced_search': True,
        },
        {
            'tier': 'weekly',
            'user_type': 'both',
            'name': 'Weekly',
            'price_monthly': Decimal('200.00'),
            'description': 'Full access for 7 days. For clients and escorts.',
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'advanced_search': True,
        },
        {
            'tier': 'premium',
            'user_type': 'both',
            'name': 'Premium',
            'price_monthly': Decimal('500.00'),
            'price_quarterly': None,
            'price_yearly': None,
            'description': 'Premium monthly access with ad-free experience and priority support.',
            'unlimited_messaging': True,
            'unlimited_content_access': True,
            'ad_free': True,
            'advanced_search': True,
            'priority_support': True,
        },
    ]
    for data in plans_data:
        _upsert_plan(SubscriptionPlan, data)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0009_merge_20260625_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[('mpesa', 'M-Pesa STK Push'), ('mpesa_till', 'M-Pesa Till')],
                default='mobile_money',
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='billing_period',
            field=models.CharField(
                choices=[
                    ('daily', 'Daily'),
                    ('weekly', 'Weekly'),
                    ('monthly', 'Monthly'),
                    ('quarterly', 'Quarterly'),
                    ('yearly', 'Yearly'),
                    ('once', 'One Time'),
                ],
                default='monthly',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='tier',
            field=models.CharField(
                choices=[
                    ('free', 'Free'),
                    ('daily', 'Daily'),
                    ('weekly', 'Weekly'),
                    ('basic', 'Basic'),
                    ('premium', 'Premium'),
                    ('vip', 'VIP'),
                    ('once', 'One Time Access'),
                ],
                max_length=20,
            ),
        ),
        migrations.RunPython(update_plans, noop),
    ]
