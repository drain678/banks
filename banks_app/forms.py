"""Forms configuration for the banks_app."""

from django import forms
from django.contrib.auth.models import User

from banks_app import config

from .models import Bank, BankAccount, Client, Transaction


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration."""

    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        """Meta class for UserRegistrationForm."""

        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        """
        Save the new user instance with an encrypted password.

        Args:
            commit (bool): If True, the user instance is saved to the database.

        Returns:
            User: The newly created user instance.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class BankAccountForm(forms.ModelForm):
    """Form for managing bank account information."""

    class Meta:
        """Meta class for BankAccountForm."""

        model = BankAccount
        fields = ['balance', 'bank']


class ClientForm(forms.ModelForm):
    """Form for managing client information."""

    banks = forms.ModelMultipleChoiceField(
        queryset=Bank.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        """Meta class for ClientForm."""

        model = Client
        fields = ['first_name', 'last_name', 'phone', 'banks']


class BankForm(forms.ModelForm):
    """Form for managing bank information."""

    class Meta:
        """Meta class for BankForm."""

        model = Bank
        fields = ['title', 'foundation_date']


class LoginForm(forms.Form):
    """Form for user login."""

    username = forms.CharField(max_length=config.MAX_LENGTH_USERNAME)
    password = forms.CharField(
        max_length=config.MIN_LENGTH_USERNAME, widget=forms.PasswordInput,
    )


class ConfirmTransactionForm(forms.ModelForm):
    """Form for confirming a transaction."""

    class Meta:
        """Meta class for ConfirmTransactionForm."""

        model = Transaction
        fields = ['amount', 'description', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
        }


class InitialTransactionForm(forms.Form):
    """Form for initiating a transaction."""

    from_bank_account_id = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        label='Select your bank account',
    )
    to_bank_account_uuid = forms.UUIDField(
        label='Recipient Bank Account UUID',
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with user-specific bank accounts.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        user = kwargs.pop('user', None)
        super(InitialTransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['from_bank_account_id'].queryset = BankAccount.objects.filter(
                client__user=user,
            )
