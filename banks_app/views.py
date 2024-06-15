"""This file contains Django views."""

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Bank, BankAccount, BankClient, Client, Transaction
from banks_app import forms, serializers


def is_admin(user):
    """
    Check if the user is an admin.

    Args:
        user (django.contrib.auth.models.User): User instance.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return user.is_superuser


def logout_view(request):
    """
    Log out the user and redirects to the homepage.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponseRedirect: Redirects to the homepage.
    """
    logout(request)
    return redirect('homepage')


@login_required
def profile_view(request):
    """
    Render and handles profile view for authenticated users.

    If user is authenticated, displays profile information, bank accounts,
    and transactions. Allows editing of client information.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders profile.html with context data.
    """
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return redirect('create_client')

    if request.method == 'POST':
        form = forms.ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return redirect('profile')
    else:
        form = forms.ClientForm(instance=client)

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
    """
    Render a list of clients.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders clients.html with context data.
    """
    clients = Client.objects.all()
    context = {
        'clients': clients,
    }
    return render(request, 'pages/clients.html', context)


@login_required
def create_client(request):
    """
    Handle client creation.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders create_client.html with form.
    """
    if request.method == 'POST':
        form = forms.ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            form.save_m2m()
            return redirect('clients')
    else:
        form = forms.ClientForm()
    return render(request, 'pages/create_client.html', {'form': form})


def register_view(request):
    """
    Handle user registration.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders register.html with form.
    """
    if request.method == 'POST':
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_client')
    else:
        form = forms.UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view using AuthenticationForm.

    Attributes:
        form_class (django.contrib.auth.forms.AuthenticationForm): Form class for authentication.
        template_name (str): Template name for rendering the login page.
    """

    form_class = AuthenticationForm
    template_name = 'registration/login.html'


@login_required
@user_passes_test(is_admin)
def delete_transaction_view(request, pk):
    """
    Delete a transaction if user is admin.

    Args:
        request (django.http.HttpRequest): Request object.
        pk (int): Primary key of the transaction to delete.

    Returns:
        django.http.HttpResponseRedirect: Redirects to 'transactions' or specified next URL.
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    return redirect(request.GET.get('next', 'transactions'))


@login_required
def confirm_transaction(request):
    """
    Confirm a transaction.

    Retrieves from and to bank accounts, validates the transaction,
    and updates balances accordingly.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders confirm_transaction.html with form and context data.
    """
    from_account_id = request.session.get('from_account_id')
    to_account_id = request.session.get('to_account_id')

    if not from_account_id or not to_account_id:
        return redirect('create_transaction')

    from_account = get_object_or_404(BankAccount, id=from_account_id)
    to_account = get_object_or_404(BankAccount, id=to_account_id)

    if request.method == 'POST':
        form = forms.ConfirmTransactionForm(request.POST)
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
        form = forms.ConfirmTransactionForm()

    return render(
        request,
        'pages/confirm_transaction.html',
        {
            'form': form,
            'from_account': from_account,
            'to_account': to_account,
        },
    )


@login_required
def create_transaction(request):
    """
    Handle creation of a transaction.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders create_transaction.html with form.
    """
    if request.method == 'POST':
        form = forms.InitialTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            from_account = form.cleaned_data['from_bank_account_id']
            to_account_uuid = form.cleaned_data['to_bank_account_uuid']

            try:
                to_account = BankAccount.objects.get(id=to_account_uuid)
                request.session['from_account_id'] = str(from_account.id)
                request.session['to_account_id'] = str(to_account.id)
                return redirect('confirm_transaction')
            except BankAccount.DoesNotExist:
                form.add_error(
                    'to_bank_account_uuid',
                    'Bank account with this UUID does not exist',
                )
        return render(request, 'pages/create_transaction.html', {'form': form})
    else:
        form = forms.InitialTransactionForm(user=request.user)
        return render(request, 'pages/create_transaction.html', {'form': form})


class UserTransactionListView(ListView):
    """
    List transactions for the logged-in user.

    Inherits from Django's ListView to display transactions.

    Attributes:
        model (django.db.models.Model): Django model for transactions.
        template_name (str): Template name for rendering the transaction list.
        context_object_name (str): Name of the context variable to use in the template.
    """

    model = Transaction
    template_name = 'pages/user_transactions.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        """
        Return a filtered queryset of Transaction objects initiated by the authenticated user.

        This method filters Transaction objects where the 'initializer' field matches
        the authenticated user making the request.

        Returns:
            django.db.models.query.QuerySet: Filtered queryset of Transaction objects.
        """
        return Transaction.objects.filter(initializer=self.request.user.client)


class TransactionDetailView(DetailView):
    """
    Detail view for displaying details of a transaction.

    Attributes:
        model (django.db.models.Model): Django model class for the transaction.
        template_name (str): Template name for rendering the transaction detail page.
        context_object_name (str): Name of the context variable containing the transaction object.
    """

    model = Transaction
    template_name = 'pages/transaction_detail.html'
    context_object_name = 'transaction'


@login_required
def transactions_view(request):
    """
    Render a list of transactions for authenticated users.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders transactions.html with context data.
    """
    transactions = Transaction.objects.all()
    context = {
        'transactions': transactions,
    }
    return render(request, 'pages/transactions.html', context)


@login_required
def bank_accounts_view(request):
    """
    Render a list of bank accounts for authenticated users.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders bank_accounts.html with context data.
    """
    bank_accounts = BankAccount.objects.all()
    context = {
        'bank_accounts': bank_accounts,
    }
    return render(request, 'pages/bank_accounts.html', context)


@login_required
def create_bank_account_view(request):
    """
    Handle creation of a bank account.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders create_bank_account.html with form.
    """
    if request.method == 'POST':
        form = forms.BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            client = Client.objects.get(user=request.user)
            bank_account.client = client
            bank_account.save()

            if not client.banks.filter(id=bank_account.bank.id).exists():
                client.banks.add(bank_account.bank)
            return redirect('profile')
    else:
        form = forms.BankAccountForm()
    return render(request, 'pages/create_bank_account.html', {'form': form})


@login_required
def delete_bank_account_view(request, pk):
    """
    Delete a bank account.

    Args:
        request (django.http.HttpRequest): Request object.
        pk (int): Primary key of the bank account to delete.

    Returns:
        django.http.HttpResponseRedirect: Redirects to 'profile' or specified next URL.
    """
    bank_account = get_object_or_404(BankAccount, pk=pk)
    bank_account.delete()
    return redirect(request.GET.get('next', 'profile'))


def homepage(request):
    """
    Render the homepage.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders index.html.
    """
    return render(request, 'index.html')


@login_required
@user_passes_test(is_admin)
def create_bank_view(request):
    """
    Handle creation of a bank if user is admin.

    Args:
        request (django.http.HttpRequest): Request object.

    Returns:
        django.http.HttpResponse: Renders create_bank.html with form.
    """
    if request.method == 'POST':
        form = forms.BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.save()
            return redirect('banks')
    else:
        form = forms.BankForm()
    return render(request, 'pages/create_bank.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_bank_view(request, pk):
    """
    Delete a bank if user is admin.

    Args:
        request (django.http.HttpRequest): Request object.
        pk (int): Primary key of the bank to delete.

    Returns:
        django.http.HttpResponseRedirect: Redirects to 'banks' or specified next URL.
    """
    bank = get_object_or_404(Bank, pk=pk)
    if request.user.is_superuser:
        bank.delete()
    return redirect(request.GET.get('next', 'banks'))


class BankListView(ListView):
    """
    ListView for listing banks.

    Attributes:
        model (django.db.models.Model): Django model class for banks.
        template_name (str): Template name for rendering the bank list page.
        context_object_name (str): Name of the context variable containing the list of banks.
    """

    model = Bank
    template_name = 'pages/banks.html'
    context_object_name = 'banks'


class BankDetailView(DetailView):
    """
    DetailView for displaying details of a bank.

    Attributes:
        model (django.db.models.Model): Django model class for the bank.
        template_name (str): Template name for rendering the bank detail page.
        context_object_name (str): Name of the context variable containing the bank object.
    """

    model = Bank
    template_name = 'pages/bank_detail.html'
    context_object_name = 'bank'


class ClientDetailView(DetailView):
    """
    DetailView for displaying details of a client.

    Attributes:
        model (django.db.models.Model): Django model class for the client.
        template_name (str): Template name for rendering the client detail page.
        context_object_name (str): Name of the context variable containing the client object.
    """

    model = Client
    template_name = 'pages/client_detail.html'
    context_object_name = 'client'


class BankViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Bank model.

    Provides API endpoints for interacting with Bank model.

    Attributes:
        queryset (django.db.models.QuerySet): QuerySet of all Bank objects.
        serializer_class (BankSerializer): Serializer class for Bank model.
    """

    queryset = Bank.objects.all()
    serializer_class = serializers.BankSerializer

    def get_permissions(self):
        """
        Return the list of permissions that this view requires.

        For 'list' and 'retrieve' actions, requires IsAuthenticated permission.
        For other actions (create, update, delete), requires IsAdminUser permission.

        Returns:
            list: List of permission instances.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Client model.

    Provides API endpoints for interacting with Client model.

    Attributes:
        queryset (django.db.models.QuerySet): QuerySet of all Client objects.
        serializer_class (ClientSerializer): Serializer class for Client model.
    """

    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Disables the delete operation for clients.

        Args:
            request (rest_framework.request.Request): Request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            rest_framework.response.Response: HTTP 405 Method Not Allowed response.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        """
        Return the list of permissions that this view requires.

        Requires IsAuthenticated permission for all actions.

        Returns:
            list: List of permission instances.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BankAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on BankAccount model.

    Provides API endpoints for interacting with BankAccount model.

    Attributes:
        queryset (django.db.models.QuerySet): QuerySet of all BankAccount objects.
        serializer_class (BankAccountSerializer): Serializer class for BankAccount model.
    """

    queryset = BankAccount.objects.all()
    serializer_class = serializers.BankAccountSerializer

    def get_permissions(self):
        """
        Return the list of permissions that this view requires based on the action.

        For 'delete', 'create', 'update' actions, requires IsAdminUser permission.
        For other actions, requires IsAuthenticated permission.

        Returns:
            list: List of permission instances.
        """
        if self.action in ['delete', 'create', 'update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BankClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on BankClient model.

    Provides API endpoints for interacting with BankClient model.

    Attributes:
        queryset (django.db.models.QuerySet): QuerySet of all BankClient objects.
        serializer_class (BankClientSerializer): Serializer class for BankClient model.
    """

    queryset = BankClient.objects.all()
    serializer_class = serializers.BankClientSerializer

    def get_permissions(self):
        """
        Return the list of permissions that this view requires based on the action.

        For 'delete', 'create', 'update' actions, requires IsAdminUser permission.
        For other actions, requires IsAuthenticated permission.

        Returns:
            list: List of permission instances.
        """
        if self.action in ['delete', 'create', 'update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Transaction model.

    Provides API endpoints for interacting with Transaction model.

    Attributes:
        queryset (django.db.models.QuerySet): QuerySet of all Transaction objects.
        serializer_class (TransactionSerializer): Serializer class for Transaction model.
    """

    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer

    def get_permissions(self):
        """
        Return the list of permissions that this view requires based on the action.

        For 'list' and 'retrieve' actions, requires IsAuthenticated permission.
        For 'create' action, checks if the initializer matches the authenticated client.
        For other actions, requires IsAdminUser permission.

        Returns:
            list: List of permission instances.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            initializer_id = self.request.data.get(
                'initializer',
            ).removeprefix('/api/client/').removesuffix('/')
            id_sender = self.request.user.client.id
            if str(id_sender) == str(initializer_id):
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
