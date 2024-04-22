from django.contrib import admin
from .models import Bank, Client, Transaction


admin.site.register(Bank)
admin.site.register(Client)
admin.site.register(Transaction)
