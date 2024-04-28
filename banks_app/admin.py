from django.contrib import admin
from .models import Bank, Client, Transaction, BankAccount, BankClient, TransactionClient, BankAccountClient


class BankAccountClientInline(admin.TabularInline):
    model = BankAccountClient
    extra = 1


class BankClientInline(admin.TabularInline):
    model = BankClient
    extra = 1


class TransactionClientInline(admin.TabularInline):
    model = TransactionClient
    extra = 1


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    model = Bank
    inlines = (BankClientInline,)
    list_display = ('title', 'foundation_date')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
    inlines = (TransactionClientInline, BankAccountClientInline)
    list_display = ('first_name', 'last_name', 'phone')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    model = BankAccount
    inlines = (BankAccountClientInline,)
    list_display = ('balance', 'client')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    inline = (TransactionClientInline,)
    list_display = ('initializer', 'amount', 'transaction_date',
                    'description', 'from_bank_account_id', 'to_bank_account_id')
    