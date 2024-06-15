"""
This module contain models for banking system.

It includes models for Bank, Client, BankAccount, Transaction and their interrelationships.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from banks_app import config

import django.core.validators as validators
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_datetime() -> datetime:
    """
    Get the current date and time.

    Returns:
        datetime: The current date and time.
    """
    return timezone.now().date()


def check_created(dt: datetime) -> None:
    """
    Check if the provided datetime is in the future.

    Args:
        dt (datetime): The datetime to check.

    Raises:
        ValidationError: If the provided datetime is in the future.
    """
    if dt > timezone.now().date():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt},
        )


class UUIDMixin(models.Model):
    """
    Abstract model mixin for UUID primary key.

    Attributes:
        id (UUIDField): Primary key, automatically generated.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        """Meta class for UUIDMixin."""

        abstract = True


class Bank(UUIDMixin):
    """
    Model represent a bank.

    Attributes:
        title (str): The name of the bank.
        foundation_date (datetime): The date the bank was founded.
        clients (ManyToManyField): The clients associated with the bank.
    """

    title = models.CharField(
        max_length=100,
        validators=[
            validators.MaxLengthValidator(
                100, message='Length title must be less than 100 symbols',
            ),
            validators.MinLengthValidator(
                1, message='Length title must be more than 0 symbol',
            ),
        ],
        unique=True,
    )

    foundation_date = models.DateField(default=get_datetime, validators=[check_created])

    clients = models.ManyToManyField('Client', through='BankClient', verbose_name=_('clients'))

    class Meta:
        """Meta class for model Bank."""

        db_table = '"banks"."bank"'
        verbose_name = _('bank')
        verbose_name_plural = _('banks')

    def __str__(self) -> str:
        """Magic method for displaying short information about Bank.

        Returns:
            str: Short information about Bank.
        """
        return f'Bank: "{self.title}", foundation_date: {self.foundation_date}'


class Client(UUIDMixin):
    """
    Model represent a client.

    Attributes:
        user (OneToOneField): The user associated with the client.
        first_name (str): The first name of the client.
        last_name (str): The last name of the client.
        phone (str): The phone number of the client.
        banks (ManyToManyField): The banks associated with the client.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=config.MAX_LENGTH_FIRST_NAME,
        validators=[
            validators.MaxLengthValidator(
                config.MAX_LENGTH_FIRST_NAME,
                message='Length first_name must be less than 70 symbols',
            ),
            validators.MinLengthValidator(
                1, message='Length first_name must be more than 0 symbol',
            ),
        ],
    )
    last_name = models.CharField(
        max_length=config.MAX_LENGTH_LAST_NAME,
        validators=[
            validators.MaxLengthValidator(
                config.MAX_LENGTH_LAST_NAME,
                message='Length last_name must be less than 100 symbols',
            ),
            validators.MinLengthValidator(
                1, message='Length last_name must be more than 0 symbol',
            ),
        ],
    )
    phone_regex = validators.RegexValidator(
        regex=r'\+7\d{10}', message='Phone number must be 10 digits in total.',
    )
    phone = models.CharField(max_length=config.MAX_LENGTH_PHONE, validators=[phone_regex])

    banks = models.ManyToManyField('Bank', through='BankClient', verbose_name=_('banks'))

    class Meta:
        """Meta class for model Client."""

        db_table = '"banks"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self) -> str:
        """Magic method for displaying short information about Client.

        Returns:
            str: Short information about Client.
        """
        return f'Client: {self.first_name} {self.last_name}, phone: {self.phone}'


class BankClient(UUIDMixin):
    """
    Model represent the relationship between a bank and a client.

    Attributes:
        bank (ForeignKey): The bank in the relationship.
        client (ForeignKey): The client in the relationship.
    """

    bank = models.ForeignKey('Bank', verbose_name=_('bank'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)

    class Meta:
        """Meta class for model BankClient."""

        db_table = '"banks"."bank_client"'
        unique_together = (
            ('bank', 'client'),
        )
        verbose_name = _('relationship bank client')
        verbose_name_plural = _('relationships bank client')

    def __str__(self) -> str:
        """Magic method for displaying information about BankClient.

        Returns:
            str: Information about BankClient.
        """
        return f'{self.bank} - {self.client}'


class BankAccount(UUIDMixin):
    """
    Model represent a bank account.

    Attributes:
        balance (DecimalField): The balance of the bank account.
        bank (ForeignKey): The bank associated with the account.
        client (ForeignKey): The client associated with the account.
    """

    balance = models.DecimalField(
        decimal_places=2, max_digits=config.MAX_DIGITS_BANK_ACCOUNT,
        validators=[validators.MinValueValidator(Decimal('0.00'))],
    )
    bank = models.ForeignKey(Bank, verbose_name=_('bank'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)

    class Meta:
        """Meta class for model BankAccount."""

        db_table = '"banks"."bank_account"'
        verbose_name = _('bank_account')
        verbose_name_plural = _('bank_accounts')

    def __str__(self) -> str:
        """Magic method for displaying short information about BankAccount.

        Returns:
            str: Short information about BankAccount.
        """
        return f'Bank_account: {self.id}, balance: {self.balance}'


class Transaction(UUIDMixin):
    """
    Model represent a transaction.

    Attributes:
        initializer (ForeignKey): The client who initiated the transaction.
        amount (DecimalField): The amount of the transaction.
        transaction_date (DateField): The date of the transaction.
        description (str): The description of the transaction.
        from_bank_account_id (ForeignKey): The source bank account.
        to_bank_account_id (ForeignKey): The destination bank account.
    """

    initializer = models.ForeignKey(Client, on_delete=models.RESTRICT, related_name='initializer')

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=config.MAX_DIGITS_AMOUNT,
        validators=[validators.MinValueValidator(Decimal('0.00'))],
    )

    transaction_date = models.DateField(default=get_datetime, validators=[check_created])

    description = models.CharField(
        null=True,
        blank=True,
        max_length=config.MAX_LENGTH_DESCRIPTION,
        validators=[
            validators.MaxLengthValidator(
                config.MAX_LENGTH_DESCRIPTION,
                message='Length description must be less than 500 symbols',
            ),
        ],
    )
    from_bank_account_id = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='sent_transactions',
    )
    to_bank_account_id = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='received_transactions',
    )

    class Meta:
        """Meta class for model Transaction."""

        db_table = '"banks"."transaction"'
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def __str__(self) -> str:
        """Magic method for displaying information about Transaction.

        Returns:
            str: Information about Transaction.
        """
        return f"Initializer: {self.initializer}, amount: {self.amount}," \
               f"description: {self.description}," \
               f"from: {self.from_bank_account_id}, to: {self.to_bank_account_id}"


class TransactionClient(UUIDMixin):
    """
    Model represent the relationship between a transaction and a client.

    Attributes:
        client (ForeignKey): The client in the relationship.
        transaction (ForeignKey): The transaction in the relationship.
    """

    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        Transaction, verbose_name=_('transaction'), on_delete=models.CASCADE,
    )

    class Meta:
        """Meta class for model TransactionClient."""

        db_table = '"banks"."transaction_client"'
        unique_together = (
            ('transaction', 'client'),
        )
        verbose_name = _('relationship transaction client')
        verbose_name_plural = _('relationships transaction client')

    def __str__(self) -> str:
        """Magic method for displaying information about TransactionClient.

        Returns:
            str: Information about TransactionClient.
        """
        return f'Transaction: {self.transaction} - {self.client}'


@receiver(post_delete, sender=BankAccount)
def delete_bank_client_relation(sender, instance, **kwargs):
    """
    Signal receiver to delete BankClient relationship when a BankAccount is deleted.

    Args:
        sender (type): The model class.
        instance (BankAccount): The instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    if not BankAccount.objects.filter(client=instance.client, bank=instance.bank).exists():
        BankClient.objects.filter(client=instance.client, bank=instance.bank).delete()
