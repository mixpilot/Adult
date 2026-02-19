# Make Standard/Premium/One-time plans visible to both client and escort (user_type='both')

from django.db import migrations


def set_plans_both(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(
        tier__in=('basic', 'premium', 'once'),
        user_type='client',
    ).update(user_type='both')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0005_create_client_plans_250_500_100'),
    ]

    operations = [
        migrations.RunPython(set_plans_both, noop),
    ]
