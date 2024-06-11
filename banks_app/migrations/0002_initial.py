# Generated by Django 5.0.3 on 2024-06-11 08:23

import banks_app.models
import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banks_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, unique=True, validators=[django.core.validators.MaxLengthValidator(100, message='Length title must be less than 100 symbols'), django.core.validators.MinLengthValidator(1, message='Length title must be more than 0 symbol')])),
                ('foundation_date', models.DateField(default=banks_app.models.get_datetime, validators=[banks_app.models.check_created])),
            ],
            options={
                'verbose_name': 'bank',
                'verbose_name_plural': 'banks',
                'db_table': '"banks"."bank"',
            },
        ),
        migrations.CreateModel(
            name='BankClient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.bank', verbose_name='bank')),
            ],
            options={
                'verbose_name': 'relationship bank client',
                'verbose_name_plural': 'relationships bank client',
                'db_table': '"banks"."bank_client"',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=70, validators=[django.core.validators.MaxLengthValidator(70, message='Length first_name must be less than 70 symbols'), django.core.validators.MinLengthValidator(1, message='Length first_name must be more than 0 symbol')])),
                ('last_name', models.CharField(max_length=100, validators=[django.core.validators.MaxLengthValidator(100, message='Length last_name must be less than 100 symbols'), django.core.validators.MinLengthValidator(1, message='Length last_name must be more than 0 symbol')])),
                ('phone', models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits in total.', regex='\\+7\\d{10}')])),
                ('banks', models.ManyToManyField(through='banks_app.BankClient', to='banks_app.bank', verbose_name='banks')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'db_table': '"banks"."client"',
            },
        ),
        migrations.AddField(
            model_name='bankclient',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='client'),
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=40, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.bank', verbose_name='bank')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='client')),
            ],
            options={
                'verbose_name': 'bank_account',
                'verbose_name_plural': 'bank_accounts',
                'db_table': '"banks"."bank_account"',
            },
        ),
        migrations.AddField(
            model_name='bank',
            name='clients',
            field=models.ManyToManyField(through='banks_app.BankClient', to='banks_app.client', verbose_name='clients'),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('transaction_date', models.DateField(default=banks_app.models.get_datetime, validators=[banks_app.models.check_created])),
                ('description', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500, message='Length description must be less than 500 symbols')])),
                ('from_bank_account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='banks_app.bankaccount')),
                ('initializer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='initializer', to='banks_app.client')),
                ('to_bank_account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_transactions', to='banks_app.bankaccount')),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
                'db_table': '"banks"."transaction"',
            },
        ),
        migrations.AlterUniqueTogether(
            name='bankclient',
            unique_together={('bank', 'client')},
        ),
        migrations.CreateModel(
            name='TransactionClient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='client')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.transaction', verbose_name='transaction')),
            ],
            options={
                'verbose_name': 'relationship transaction client',
                'verbose_name_plural': 'relationships transaction client',
                'db_table': '"banks"."transaction_client"',
                'unique_together': {('transaction', 'client')},
            },
        ),
    ]
