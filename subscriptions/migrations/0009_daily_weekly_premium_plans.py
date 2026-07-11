# Pricing update: Daily 150, Weekly 200, Premium monthly 500 (buyers & sellers)

from decimal import Decimal
from django.db import migrations, models


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
        ('subscriptions', '0008_alter_payment_payment_method'),
    ]

    operations = [
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
