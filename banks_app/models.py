from django.db import models


class Bank(models.Model):
    title = models.CharField(max_length=200)
    foundation_date = models.DateTimeField()


class Client(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    banks = models.ManyToManyField(Bank)


class Transaction(models.Model):
    amount = models.DecimalField(decimal_places=2, max_digits=30)
    date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    sender = models.ForeignKey(Client, on_delete=models.RESTRICT, related_name='sent_transactions')
    receiver = models.ForeignKey(Client, on_delete=models.RESTRICT, related_name='received_transactions')
