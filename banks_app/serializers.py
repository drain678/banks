from rest_framework import serializers
from .models import Bank, Client, BankAccount, Transaction
from django.utils import timezone


def check_created(dt):
    return dt > timezone.now().date()


class BankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    foundation_date = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Client
        fields = '__all__'

    def validate(self, data):
        if check_created(data['foundation_date']):
            raise serializers.ValidationError(
                'Foundation date cannot be in the future')
        return super().validate(data)


class BankAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    transaction_date = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Transaction
        fields = '__all__'

    def validate(self, data):
        if check_created(data['transaction_date']):
            raise serializers.ValidationError(
                'Transaction date cannot be in the future')
        return super().validate(data)
