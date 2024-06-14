"""File with admin interface."""

from django.contrib import admin

import models


class BankAccountInline(admin.TabularInline):
    """Inline definition for displaying and editing BankAccount objects."""

    model = models.BankAccount
    extra = 1


class BankClientInline(admin.TabularInline):
    """Inline definition for displaying and editing BankClient objects."""

    model = models.BankClient
    extra = 1


class TransactionClientInline(admin.TabularInline):
    """Inline definition for displaying and editing TransactionClient objects."""

    model = models.TransactionClient
    extra = 1


@admin.register(models.Bank)
class BankAdmin(admin.ModelAdmin):
    """Admin interface definition for the Bank model."""

    model = models.Bank
    inlines = (BankClientInline,)
    list_display = ('title', 'foundation_date')


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin interface definition for the Client model."""

    model = models.Client
    inlines = (TransactionClientInline, BankAccountInline)
    list_display = ('first_name', 'last_name', 'phone')


@admin.register(models.BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """Admin interface definition for the BankAccount model."""

    list_display = ('id', 'balance', 'bank', 'client')
    search_fields = ('id', 'balance')
    model = models.BankAccount


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface definition for the Transaction model."""

    model = models.Transaction
    inline = (TransactionClientInline,)
    list_display = (
        'initializer',
        'amount',
        'transaction_date',
        'description',
        'from_bank_account_id',
        'to_bank_account_id',
    )
