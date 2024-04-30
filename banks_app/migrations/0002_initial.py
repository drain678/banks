# Generated by Django 5.0.3 on 2024-04-30 10:36

import banks_app.models
import datetime
import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banks_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, validators=[django.core.validators.MaxLengthValidator(100, message='Length title must be less than 100 symbols'), django.core.validators.MinLengthValidator(1, message='Length title must be more than 0 symbol')])),
                ('foundation_date', models.DateField(default=datetime.date(2024, 4, 30), validators=[banks_app.models.check_created])),
            ],
            options={
                'verbose_name': 'bank',
                'verbose_name_plural': 'banks',
                'db_table': '"banks"."bank"',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=70, validators=[django.core.validators.MaxLengthValidator(70, message='Length first_name must be less than 70 symbols'), django.core.validators.MinLengthValidator(1, message='Length first_name must be more than 0 symbol')])),
                ('last_name', models.CharField(max_length=100, validators=[django.core.validators.MaxLengthValidator(100, message='Length last_name must be less than 100 symbols'), django.core.validators.MinLengthValidator(1, message='Length last_name must be more than 0 symbol')])),
                ('phone', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits.', regex='^\\d{10}$')])),
                ('banks', models.ManyToManyField(to='banks_app.bank')),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'db_table': '"banks"."client"',
                'ordering': ['first_name', 'last_name', 'phone'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=40, validators=[django.core.validators.MaxValueValidator(1000000000), django.core.validators.MinValueValidator(0)])),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client')),
            ],
            options={
                'verbose_name': 'bank_account',
                'verbose_name_plural': 'bank_accounts',
                'db_table': '"banks"."bank_account"',
                'ordering': ['balance', 'client'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(10000000000000000000)])),
                ('transaction_date', models.DateField(default=datetime.date(2024, 4, 30), validators=[banks_app.models.check_created])),
                ('description', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500, message='Length description must be less than 500 symbols')])),
                ('from_bank_account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='banks_app.bankaccount')),
                ('initializer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='initializer', to='banks_app.client')),
                ('to_bank_account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_transactions', to='banks_app.bankaccount')),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
                'db_table': '"banks"."transaction"',
                'ordering': ['initializer', 'amount', 'transaction_date', 'description', 'from_bank_account_id', 'to_bank_account_id'],
            },
        ),
        migrations.CreateModel(
            name='BankClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.bank', verbose_name='bank')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='client')),
            ],
            options={
                'verbose_name': 'relationship bank client',
                'verbose_name_plural': 'relationships bank client',
                'db_table': '"banks"."bank_client"',
                'unique_together': {('bank', 'client')},
            },
        ),
        migrations.CreateModel(
            name='BankAccountClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.bankaccount', verbose_name='bank_account')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='client')),
            ],
            options={
                'verbose_name': 'relationship bank_account client',
                'verbose_name_plural': 'relationships bank_account client',
                'db_table': '"banks"."bank_account_client"',
                'unique_together': {('bank_account', 'client')},
            },
        ),
        migrations.CreateModel(
            name='TransactionClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.client', verbose_name='transaction')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banks_app.transaction', verbose_name='client')),
            ],
            options={
                'verbose_name': 'relationship transaction client',
                'verbose_name_plural': 'relationships transaction client',
                'db_table': '"banks"."transaction_client"',
                'unique_together': {('transaction', 'client')},
            },
        ),
    ]