from rest_framework import viewsets
from .models import Bank, BankClient, Client, BankAccount, Transaction
from .serializers import BankClientSerializer, BankSerializer, ClientSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from .forms import ClientForm, ConfirmTransactionForm, InitialTransactionForm, UserRegistrationForm, BankForm, BankAccountForm
from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_superuser


def logout_view(request):
    logout(request)
    return redirect('homepage')


@login_required
def profile_view(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return redirect('create_client')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return redirect('profile')
    else:
        form = ClientForm(instance=client)

    banks = Bank.objects.filter(bankclient__client=client) if client else []
    bank_accounts = BankAccount.objects.filter(client=client) if client else []
    transactions = Transaction.objects.filter(initializer=client) if client else []

    context = {
        'client': client,
        'form': form,
        'banks': banks,
        'bank_accounts': bank_accounts,
        'transactions': transactions,
    }

    return render(request, 'pages/profile.html', context)


@login_required
def clients_view(request):
    clients = Client.objects.all()
    context = {
        'clients': clients,
    }
    return render(request, 'pages/clients.html', context)


@login_required
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            form.save_m2m()
            return redirect('clients')
    else:
        form = ClientForm()
    return render(request, 'pages/create_client.html', {'form': form})



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_client')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'


@login_required
@user_passes_test(is_admin)
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    return redirect(request.GET.get('next', 'transactions'))


@login_required
def confirm_transaction(request):
    from_account_id = request.session.get('from_account_id')
    to_account_id = request.session.get('to_account_id')

    if not from_account_id or not to_account_id:
        return redirect('create_transaction')

    from_account = get_object_or_404(BankAccount, id=from_account_id)
    to_account = get_object_or_404(BankAccount, id=to_account_id)

    if request.method == 'POST':
        form = ConfirmTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.from_bank_account_id = from_account
            transaction.to_bank_account_id = to_account
            transaction.initializer = request.user.client

            if from_account.balance < transaction.amount:
                form.add_error('amount', 'Insufficient funds in your account')
            elif transaction.amount < 0:
                form.add_error('amount', 'Amount cannot be negative')
            else:
                from_account.balance -= transaction.amount
                to_account.balance += transaction.amount
                from_account.save()
                to_account.save()
                transaction.save()
                return redirect('profile')
    else:
        form = ConfirmTransactionForm()

    return render(request, 'pages/confirm_transaction.html', {'form': form, 'from_account': from_account, 'to_account': to_account})


@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = InitialTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            from_account = form.cleaned_data['from_bank_account_id']
            to_account_uuid = form.cleaned_data['to_bank_account_uuid']

            try:
                to_account = BankAccount.objects.get(id=to_account_uuid)
                request.session['from_account_id'] = str(from_account.id)
                request.session['to_account_id'] = str(to_account.id)
                return redirect('confirm_transaction')
            except BankAccount.DoesNotExist:
                form.add_error('to_bank_account_uuid',
                               'Bank account with this UUID does not exist')
        return render(request, 'pages/create_transaction.html', {'form': form})
    else:
        form = InitialTransactionForm(user=request.user)
        return render(request, 'pages/create_transaction.html', {'form': form})
    
class UserTransactionListView(ListView):
    model = Transaction
    template_name = 'pages/user_transactions.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(initializer=self.request.user)


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'pages/transaction_detail.html'
    context_object_name = 'transaction'


@login_required
def transactions_view(request):
    transactions = Transaction.objects.all()
    context = {
        'transactions': transactions,
    }
    return render(request, 'pages/transactions.html', context)


@login_required
def bank_accounts_view(request):
    bank_accounts = BankAccount.objects.all()
    context = {
        'bank_accounts': bank_accounts,
    }
    return render(request, 'pages/bank_accounts.html', context)


@login_required
def create_bank_account_view(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            client = Client.objects.get(user=request.user)
            bank_account.client = client
            bank_account.save()

            if not client.banks.filter(id=bank_account.bank.id).exists():
                client.banks.add(bank_account.bank)
            return redirect('profile')
    else:
        form = BankAccountForm()
    return render(request, 'pages/create_bank_account.html', {'form': form})


@login_required
def delete_bank_account_view(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    bank_account.delete()
    return redirect(request.GET.get('next', 'profile'))


def homepage(request):
    return render(request, 'index.html')


@login_required
@user_passes_test(is_admin)
def create_bank_view(request):
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.save()
            return redirect('banks')
    else:
        form = BankForm()
    return render(request, 'pages/create_bank.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_bank_view(request, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.user.is_superuser:
        bank.delete()
    return redirect(request.GET.get('next', 'banks'))


class BankListView(ListView):
    model = Bank
    template_name = 'pages/banks.html'
    context_object_name = 'banks'


class ClientListView(ListView):
    model = Client
    template_name = 'pages/clients.html'
    context_object_name = 'clients'


class BankDetailView(DetailView):
    model = Bank
    template_name = 'pages/bank_detail.html'
    context_object_name = 'bank'


class ClientDetailView(DetailView):
    model = Client
    template_name = 'pages/client_detail.html'
    context_object_name = 'client'


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
   
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
       

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_permissions(self):
        if self.action in ['delete', 'create', 'update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    

class BankClientViewSet(viewsets.ModelViewSet):
    queryset = BankClient.objects.all()
    serializer_class = BankClientSerializer

    def get_permissions(self):
        if self.action in ['delete', 'create', 'update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            initializer_id = self.request.data.get('initializer').removeprefix('/api/client/').removesuffix('/')
            # print(self.request.user.client.id)
            # print('***********************************')
            id_sender = self.request.user.client.id
            if str(id_sender) == str(initializer_id):
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
