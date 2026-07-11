# Merge parallel 0008 migrations (M-Pesa branch + Paystack branch).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0008_alter_payment_payment_method'),
        ('subscriptions', '0008_alter_payment_payment_method_and_more'),
    ]

    operations = []
