from django.contrib import admin
from .models import Bank, Client, Transaction, Bank_account


admin.site.register(Bank)
admin.site.register(Client)
admin.site.register(Transaction)
admin.site.register(Bank_account)
