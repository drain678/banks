from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4


class Bank(models.Model):
    title = models.CharField(max_length=200)
    foundation_date = models.DateField()

    class Meta:
        db_table = '"banks"."bank"'
        ordering = ['title']
        verbose_name = _('bank')
        verbose_name_plural = _('banks')

    def __str__(self) -> str:
        return f'"{self.title}", foundation_date: {self.foundation_date}'


class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    banks = models.ManyToManyField(Bank)

    class Meta:
        db_table = '"banks"."client"'
        ordering = ['first_name', 'last_name', 'phone']
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} {self.phone}'
    

class BankClient(models.Model):
    bank = models.ForeignKey(Bank, verbose_name=_(
        'bank'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_(
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


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    balance = models.DecimalField(decimal_places=2, max_digits=40)
    client = models.OneToOneField(Client, on_delete=models.CASCADE)

    class Meta:
        db_table = '"banks"."bank_account"'
        ordering = ['balance', 'client']
        verbose_name = _('bank_account')
        verbose_name_plural = _('bank_accounts')

    def __str__(self) -> str:
        return f'{self.balance} {self.client}'


class BankAccountClient(models.Model):
    bank_account = models.ForeignKey(BankAccount, verbose_name=_('bank_account'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.bank_account} - {self.client}'

    class Meta:
        db_table = '"banks"."bank_account_client"'
        unique_together = (
            ('bank_account', 'client'),
        )
        verbose_name = _('relationship bank_account client')
        verbose_name_plural = _('relationships bank_account client')


class Transaction(models.Model):
    initializer = models.ForeignKey(Client, on_delete=models.RESTRICT, related_name='initializer')
    amount = models.DecimalField(decimal_places=2, max_digits=30)
    transaction_date = models.DateField()
    description = models.CharField(max_length=1000)
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
        return f'Initializer: {self.initializer}, {self.description}, from: {self.from_bank_account_id}, to: {self.to_bank_account_id}'


class TransactionClient(models.Model):
    client = models.ForeignKey(Client, verbose_name=_('transaction'), on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, verbose_name=_('client'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.transaction} - {self.client}'

    class Meta:
        db_table = '"banks"."transaction_client"'
        unique_together = (
            ('transaction', 'client'),
        )
        verbose_name = _('relationship transaction client')
        verbose_name_plural = _('relationships transaction client')
