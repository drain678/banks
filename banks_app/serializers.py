"""This file defines serializers for various models related to banking operations."""

from rest_framework import serializers

from .models import Bank, BankAccount, BankClient, Client, Transaction


class BankSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Bank model."""

    class Meta:
        """Meta class for BankSerializer."""

        model = Bank
        fields = '__all__'


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Client model."""

    class Meta:
        """Meta class for ClientSerializer."""

        model = Client
        exclude = ['user']

    def create(self, validated_data):
        """
        Create and return a new Client instance, associating it with the current user.

        Args:
            validated_data (dict): Validated data received for client creation.

        Returns:
            Client: Newly created Client instance associated with the current user.
        """
        user = self.context['request'].user
        return Client.objects.create(
            user=user,
            **validated_data,
        )


class BankAccountSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for BankAccount model."""

    class Meta:
        """Meta class for BankAccountSerializer."""

        model = BankAccount
        fields = '__all__'


class BankClientSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for BankClient model."""

    class Meta:
        """Meta class for BankClientSerializer."""

        model = BankClient
        fields = '__all__'


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Transaction model."""

    class Meta:
        """Meta class for TransactionSerializer."""

        model = Transaction
        fields = '__all__'
