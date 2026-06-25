from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_subscriptionplan_earnings_tracking_and_more'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='C2bTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_id', models.CharField(db_index=True, max_length=50, unique=True)),
                ('trans_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('trans_time', models.CharField(blank=True, max_length=20)),
                ('business_shortcode', models.CharField(blank=True, max_length=20)),
                ('bill_ref_number', models.CharField(blank=True, db_index=True, max_length=100)),
                ('msisdn', models.CharField(blank=True, db_index=True, max_length=20)),
                ('transaction_type', models.CharField(blank=True, max_length=50)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('raw_payload', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='c2b_transactions', to='subscriptions.payment')),
            ],
            options={
                'verbose_name': 'C2B transaction',
                'verbose_name_plural': 'C2B transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
