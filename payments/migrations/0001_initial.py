# Generated migration for payments (M-Pesa) app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MpesaTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_reference', models.CharField(db_index=True, help_text='Our reference, e.g. sub_<payment_id> for subscription payment', max_length=64)),
                ('transaction_desc', models.CharField(blank=True, max_length=256)),
                ('phone_number', models.CharField(max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='KES', max_length=3)),
                ('checkout_request_id', models.CharField(blank=True, max_length=100, unique=True)),
                ('merchant_request_id', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('mpesa_receipt_number', models.CharField(blank=True, max_length=50)),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_description', models.CharField(blank=True, max_length=512)),
                ('callback_metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'M-Pesa transaction',
                'verbose_name_plural': 'M-Pesa transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
