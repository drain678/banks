from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import CharField

from .models import Bank, BankAccount, Client, Transaction


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['balance', 'bank']


class ClientForm(forms.ModelForm):
    banks = forms.ModelMultipleChoiceField(
        queryset=Bank.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'phone', 'banks']


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['title', 'foundation_date']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['amount', 'description', 'from_bank_account_id', 'to_bank_account_id', 'transaction_date']

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super(TransactionForm, self).__init__(*args, **kwargs)
#         if user:
#             self.fields['from_bank_account_id'].queryset = BankAccount.objects.filter(
#                 client__user=user)


class ConfirmTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'})
        }


class InitialTransactionForm(forms.Form):
    from_bank_account_id = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        label='Select your bank account'
    )
    to_bank_account_uuid = forms.UUIDField(
        label='Recipient Bank Account UUID'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InitialTransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['from_bank_account_id'].queryset = BankAccount.objects.filter(
                client__user=user)
