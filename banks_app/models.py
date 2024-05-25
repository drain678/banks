from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save



def get_datetime() -> datetime:
    return timezone.now().date()


def check_created(dt: datetime) -> None:
    if dt > timezone.now().date():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt}
        )


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Bank(UUIDMixin):
    title = models.CharField(
        max_length=100,
        validators=[
            MaxLengthValidator(
                100, message='Length title must be less than 100 symbols'),
            MinLengthValidator(
                1, message='Length title must be more than 0 symbol')
        ],
        unique=True,
    )
    foundation_date = models.DateField(
        default=get_datetime, validators=[check_created])
    clients = models.ManyToManyField('Client', through='BankClient', verbose_name=_(
        'clients'))
    
    class Meta:
        db_table = '"banks"."bank"'
        verbose_name = _('bank')
        verbose_name_plural = _('banks')

    def __str__(self) -> str:
        return f'Bank: "{self.title}", foundation_date: {self.foundation_date}'


class Client(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=70,
        validators=[
            MaxLengthValidator(
                70, message='Length first_name must be less than 70 symbols'),
            MinLengthValidator(
                1, message='Length first_name must be more than 0 symbol')
        ],
    )
    last_name = models.CharField(
        max_length=100,
        validators=[
            MaxLengthValidator(
                100, message='Length last_name must be less than 100 symbols'),
            MinLengthValidator(
                1, message='Length last_name must be more than 0 symbol')
        ],
    )
    phone_regex = RegexValidator(
        regex=r'\+7\d{10}', message='Phone number must be 10 digits in total.')
    phone = models.CharField(max_length=12, validators=[phone_regex])

    banks = models.ManyToManyField('Bank', through='BankClient', verbose_name=_(
        'banks'))

    class Meta:
        db_table = '"banks"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self) -> str:
        return f'Client: {self.first_name} {self.last_name}, phone: {self.phone}'


class BankClient(UUIDMixin):
    bank = models.ForeignKey('Bank', verbose_name=_(
        'bank'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_(
        'client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.bank} - {self.client}'

    class Meta:
        db_table = '"banks"."bank_client"'
        unique_together = (
            ('bank', 'client'),
        )
        verbose_name = _('relationship bank client')
        verbose_name_plural = _('relationships bank client')


class BankAccount(UUIDMixin):
    balance = models.DecimalField(decimal_places=2, max_digits=40, validators=[MinValueValidator(0)])
    client = models.OneToOneField(BankClient, on_delete=models.CASCADE)

    class Meta:
        db_table = '"banks"."bank_account"'
        verbose_name = _('bank_account')
        verbose_name_plural = _('bank_accounts')

    def __str__(self) -> str:
        return f'Bank_account: {self.client.first_name}, balance: {self.balance}'


class BankAccountClient(UUIDMixin):
    bank_account = models.ForeignKey(BankAccount, verbose_name=_(
        'bank_account'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_(
        'client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.client} - {self.bank_account}'

    class Meta:
        db_table = '"banks"."bank_account_client"'
        unique_together = (
            ('bank_account', 'client'),
        )
        verbose_name = _('relationship bank_account client')
        verbose_name_plural = _('relationships bank_account client')


class Transaction(UUIDMixin):
    initializer = models.ForeignKey(
        Client, on_delete=models.RESTRICT, related_name='initializer')
    amount = models.FloatField(validators=[MinValueValidator(0.01)])
    transaction_date = models.DateField(
        default=get_datetime, validators=[check_created])
    description = models.CharField(
        null=True,
        blank=True,
        max_length=500,
        validators=[
            MaxLengthValidator(
                500, message='Length description must be less than 500 symbols'),
        ],
    )
    from_bank_account_id = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name='sent_transactions')
    to_bank_account_id = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name='received_transactions')

    class Meta:
        db_table = '"banks"."transaction"'
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def __str__(self) -> str:
        return f'Initializer: {self.initializer}, description: {self.description}, from: {self.from_bank_account_id}, to: {self.to_bank_account_id}'


class TransactionClient(UUIDMixin):
    client = models.ForeignKey(Client, verbose_name=_(
        'client'), on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        Transaction, verbose_name=_('transaction'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'Transaction: {self.transaction} - {self.client}'

    class Meta:
        db_table = '"banks"."transaction_client"'
        unique_together = (
            ('transaction', 'client'),
        )
        verbose_name = _('relationship transaction client')
        verbose_name_plural = _('relationships transaction client')
