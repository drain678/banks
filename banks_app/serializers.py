from rest_framework import serializers
from .models import Bank, Client, BankAccount, Transaction


class BankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        exclude = ['user'] # TODO: add user to GET responses 
        
    
    def create(self, validated_data):
      user = self.context['request'].user
      client = Client.objects.create(
         user=user,
         **validated_data
      )
      return client
    

class BankAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
