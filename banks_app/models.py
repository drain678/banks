from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone


def get_datetime() -> datetime:
    return timezone.now().date()


def check_created(dt: datetime) -> None:
    if dt > timezone.now().date():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt}
        )


class Bank(models.Model):
    title = models.CharField(
        max_length=100,
        validators=[
            MaxLengthValidator(100, message='Length title must be less than 100 symbols'),
            MinLengthValidator(1, message='Length title must be more than 0 symbol')
        ],
        unique=True,
    )
    foundation_date = models.DateField(default=get_datetime(), validators=[check_created])

    class Meta:
        db_table = '"banks"."bank"'
        ordering = ['title']
        verbose_name = _('bank')
        verbose_name_plural = _('banks')

    def __str__(self) -> str:
        return f'Bank: "{self.title}", foundation_date: {self.foundation_date}'


class Client(models.Model):
    first_name = models.CharField(
        max_length=70,
        validators=[
            MaxLengthValidator(70, message='Length first_name must be less than 70 symbols'),
            MinLengthValidator(1, message='Length first_name must be more than 0 symbol')
        ],
    )
    last_name = models.CharField(
        max_length=100,
        validators=[
            MaxLengthValidator(100, message='Length last_name must be less than 100 symbols'),
            MinLengthValidator(1, message='Length last_name must be more than 0 symbol')
        ],
    )
    phone_regex = RegexValidator(regex=r'\+7\d{10}', message='Phone number must be 10 digits in total.')
    phone = models.CharField(max_length=12, validators=[phone_regex])
    
    banks = models.ManyToManyField(Bank)

    class Meta:
        db_table = '"banks"."client"'
        ordering = ['first_name', 'last_name', 'phone']
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self) -> str:
        return f'Client: {self.first_name} {self.last_name}, phone: {self.phone}'
    

class BankClient(models.Model):
    bank = models.ForeignKey(Bank, verbose_name=_('bank'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.bank} - {self.client}'

    class Meta:
        db_table = '"banks"."bank_client"'
        unique_together = (
            ('bank', 'client'),
        )
        verbose_name = _('relationship bank client')
        verbose_name_plural = _('relationships bank client')


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    balance = models.DecimalField(decimal_places=2, max_digits=40, validators=[MaxValueValidator(1000000000), MinValueValidator(0)])
    client = models.OneToOneField(Client, on_delete=models.CASCADE)

    class Meta:
        db_table = '"banks"."bank_account"'
        ordering = ['balance', 'client']
        verbose_name = _('bank_account')
        verbose_name_plural = _('bank_accounts')

    def __str__(self) -> str:
        return f'Bank_account: {self.id}, balance: {self.balance}'


class BankAccountClient(models.Model):
    bank_account = models.ForeignKey(BankAccount, verbose_name=_('bank_account'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.client} - {self.bank_account}'

    class Meta:
        db_table = '"banks"."bank_account_client"'
        unique_together = (
            ('bank_account', 'client'),
        )
        verbose_name = _('relationship bank_account client')
        verbose_name_plural = _('relationships bank_account client')


class Transaction(models.Model):
    initializer = models.ForeignKey(Client, on_delete=models.RESTRICT, related_name='initializer')
    amount = models.FloatField(validators=[MinValueValidator(0.01)])
    transaction_date = models.DateField(default=get_datetime(), validators=[check_created])
    description = models.CharField(
        null=True,
        blank=True,
        max_length=500,
        validators=[
            MaxLengthValidator(500, message='Length description must be less than 500 symbols'),
        ],
    )
    from_bank_account_id = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sent_transactions')
    to_bank_account_id = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='received_transactions')

    class Meta:
        db_table = '"banks"."transaction"'
        ordering = [
            'initializer',
            'amount',
            'transaction_date',
            'description',
            'from_bank_account_id',
            'to_bank_account_id',
        ]
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def __str__(self) -> str:
        return f'Initializer: {self.initializer}, description: {self.description}, from: {self.from_bank_account_id}, to: {self.to_bank_account_id}'


class TransactionClient(models.Model):
    client = models.ForeignKey(Client, verbose_name=_('transaction'), on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, verbose_name=_('client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'Transaction: {self.transaction} - {self.client}'

    class Meta:
        db_table = '"banks"."transaction_client"'
        unique_together = (
            ('transaction', 'client'),
        )
        verbose_name = _('relationship transaction client')
        verbose_name_plural = _('relationships transaction client')
