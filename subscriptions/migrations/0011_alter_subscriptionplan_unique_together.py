# Enforce unique (tier, user_type) after removing duplicate rows from legacy data.

from django.db import migrations


def dedupe_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    Subscription = apps.get_model('subscriptions', 'Subscription')
    Payment = apps.get_model('subscriptions', 'Payment')

    keepers = {}
    for plan in SubscriptionPlan.objects.order_by('id'):
        key = (plan.tier, plan.user_type)
        if key in keepers:
            keeper = keepers[key]
            Subscription.objects.filter(plan_id=plan.id).update(plan_id=keeper.id)
            Payment.objects.filter(plan_id=plan.id).update(plan_id=keeper.id)
            plan.delete()
        else:
            keepers[key] = plan


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0010_daily_weekly_premium_plans'),
    ]

    operations = [
        migrations.RunPython(dedupe_subscription_plans, noop),
        migrations.AlterUniqueTogether(
            name='subscriptionplan',
            unique_together={('tier', 'user_type')},
        ),
    ]
