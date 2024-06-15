"""File with tests for API."""

import json
from decimal import Decimal

from tests import config
from banks_app.models import Bank, BankAccount, Client, Transaction
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class BanksAPITest(TestCase):
    """Test suite for the Banks API."""

    def setUp(self):
        """Set up the test client, user, and superuser for testing."""
        self.api_client = APIClient()
        # users
        self.user = User.objects.create_user(username='user', password='user')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
        # tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)

    def test_bank_creation(self):
        """Test the creation of a bank, checking status codes, headers, and bank details."""
        # проверка статус кода на создание банка
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {'title': config.TEST_TITLE}
        response = self.api_client.post('/api/bank/', body)
        self.assertEqual(response.status_code, config.CREATED)

        # проверка на то, что банк действительно создался
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)

        # проверка получения банка обычного пользователя
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)

        # проверка заголовков
        self.assertEqual(self.api_client.head(url).status_code, config.OK)

        # проверка на то, что у банка правильное название
        resp_body = json.loads(response.content.decode())
        self.assertEqual(resp_body['title'], config.TEST_TITLE)

        # проверка на то, что этот банк среди других банков
        response = self.api_client.get('/api/bank/')
        self.assertEqual(response.status_code, config.OK)
        resp_body = json.loads(response.content.decode())
        bank_titles = [b['title'] for b in resp_body]
        self.assertIn(
            config.TEST_TITLE,
            bank_titles,
            f'bank was not found in /api/bank/, response: {resp_body}',
        )

    def test_bank_403(self):
        """Test the forbidden response when a regular user attempts to create a bank."""
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        response = self.api_client.post('/api/bank/', {'title': config.TEST_TITLE})
        self.assertEqual(response.status_code, config.FORBIDDEN)

    def test_bank_creation_duplicate_title(self):
        """Test the creation of a bank with a duplicate title."""
        Bank.objects.create(title=config.TEST_TITLE)
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {'title': config.TEST_TITLE}
        response = self.api_client.post('/api/bank/', body)
        self.assertEqual(response.status_code, config.BAD_REQUEST)

    def test_bank_delete(self):
        """Test the deletion of a bank by a superuser."""
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {'title': config.TEST_TITLE}
        response = self.api_client.post('/api/bank/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, config.NO_CONTENT)

    def test_bank_update(self):
        """Test the update of a bank by a superuser."""
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {'title': config.TEST_TITLE}
        response = self.api_client.post('/api/bank/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['title'] = 'Banka_ogurcov'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, config.OK)


class ClientsAPITest(TestCase):
    """Test suite for the Clients API."""

    def setUp(self):
        """Set up the test client, user, and superuser for testing."""
        self.api_client = APIClient()
        # users
        self.user = User.objects.create_user(username='user', password='user')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
        # tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)

    def test_client_creation(self):
        """Test the creation of clients by both superuser and regular user."""
        # проверка созданния супер пользователя
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = config.CLIENT_BUSIK
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        # проверка получения супер пользователя
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        id = url.removeprefix('/api/client/').removesuffix('/')
        client = Client.objects.filter(id=id).first()
        self.assertEqual(client.user, self.superuser)
        # проверка создания обычного пользователя
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        body = config.CLIENT_STESHA
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        # проверка получения обычного пользователя
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        id = url.removeprefix('/api/client/').removesuffix('/')
        client = Client.objects.filter(id=id).first()
        self.assertEqual(client.user, self.user)
        # проверка заголовков
        self.assertEqual(self.api_client.head(url).status_code, config.OK)

    def test_client_delete(self):
        """Test the forbidden response when attempting to delete a client."""
        # проверка удаления от супер пользователя
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = config.CLIENT_BUSIK
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, config.METOD_NOT_ALLOWED)
        # проверка удаления от обычного пользователя
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        body = config.CLIENT_STESHA
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, config.METOD_NOT_ALLOWED)

    def test_client_update(self):
        """Test the update of client details by both superuser and regular user."""
        # проверка обновления супер пользователя
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = config.CLIENT_BUSIK
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['first_name'] = 'Pusik'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, config.OK)
        # проверка обновления обычного пользователя
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        body = config.CLIENT_STESHA
        response = self.api_client.post('/api/client/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['first_name'] = 'Steshik'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, config.OK)


class BankAccountAPITest(TestCase):
    """Test suite for the Bank Accounts API."""

    def setUp(self):
        """Set up the test client, user, superuser, and necessary data for testing."""
        self.api_client = APIClient()
        # users
        self.user = User.objects.create_user(username='user', password='user')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
        # tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
        # creating bank
        self.bank = Bank.objects.create(title=config.TEST_TITLE, foundation_date=timezone.now().date())
        # creating client
        self.client_instance = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Testovich',
            phone='+79000000000',
        )

    def test_bank_account_creation(self):
        """Test the creation of bank accounts by a superuser."""
        # проверка создания банковского счёта суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'balance': 1000.00, 'bank': f'/api/bank/{self.bank.id}/',
            'client': f'/api/client/{self.client_instance.id}/',
        }
        response = self.api_client.post('/api/bank_account/', body)
        self.assertEqual(response.status_code, config.CREATED)
        # проверка получения созданного банковского счёта суперпользователем
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)
        # проверка на зачисление верной суммы
        bank_account_id = url.removeprefix('/api/bank_account/').removesuffix('/')
        bank_account = BankAccount.objects.get(id=bank_account_id)
        self.assertEqual(bank_account.balance, 1000.00)
        # проверка заголовков
        self.assertEqual(self.api_client.head(url).status_code, config.OK)
        # проверка получения созданного банковского счёта обычным пользователем
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)

    def test_bank_account_update(self):
        """Test the update of bank account details by a superuser."""
        # обновленние банковского счёта суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'balance': '1000.00',
            'bank': f'/api/bank/{self.bank.id}/',
            'client': f'/api/client/{self.client_instance.id}/',
        }
        response = self.api_client.post('/api/bank_account/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['balance'] = '2000.0'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, config.OK)
        # проверка обновления банковского счёта
        bank_account_id = url.removeprefix('/api/bank_account/').removesuffix('/')
        bank_account = BankAccount.objects.get(id=bank_account_id)
        self.assertEqual(bank_account.balance, config.NEW_BALANCE)

    def test_bank_account_delete(self):
        """Test the deletion of a bank account by a superuser."""
        # удаление банковского счёта суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'balance': '1000.00',
            'bank': f'/api/bank/{self.bank.id}/',
            'client': f'/api/client/{self.client_instance.id}/',
        }
        response = self.api_client.post('/api/bank_account/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, config.NO_CONTENT)
        # проверка удаления банковского счёта
        id = url.removeprefix('/api/bank_account/').removesuffix('/')
        self.assertFalse(BankAccount.objects.filter(id=id).exists())

    def test_bank_account_403(self):
        """Test that a regular user cannot create a bank account."""
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        body = {
            'balance': '1000.00',
            'bank': f'/api/bank/{self.bank.id}/',
            'client': f'/api/client/{self.client_instance.id}/',
        }
        response = self.api_client.post('/api/bank_account/', body)
        self.assertEqual(response.status_code, config.FORBIDDEN)


class TransactionAPITest(TestCase):
    """A TestCase for testing the Transaction API endpoints."""

    def setUp(self):
        """Set up the test client, users, and necessary data for testing transactions."""
        self.api_client = APIClient()
        # users
        self.user = User.objects.create_user(username='user', password='user')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
        # tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
        # creating bank
        self.bank = Bank.objects.create(title=config.TEST_TITLE, foundation_date=timezone.now().date())
        # creating client
        self.client_instance_1 = Client.objects.create(
            user=self.superuser,
            first_name='Test1',
            last_name='Testovich1',
            phone='+79000000001',
        )
        # сreating bank accounts
        self.bank_account_1 = BankAccount.objects.create(
            balance=Decimal('1000.00'), bank=self.bank, client=self.client_instance_1,
        )
        self.bank_account_2 = BankAccount.objects.create(
            balance=Decimal('2000.00'), bank=self.bank, client=self.client_instance_1,
        )

    def test_transaction_creation(self):
        """Test the creation of a transaction by a superuser."""
        # создание транзакции для суперпользователя
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/',
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, config.CREATED)
        # проверка получения созданного банковского счёта суперпользователем
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)
        # проверка заголовков
        self.assertEqual(self.api_client.head(url).status_code, config.OK)

    def test_transaction_update(self):
        """Test the update of a transaction by a superuser."""
        # обновление транзакции суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/',
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['amount'] = '1000.00'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, config.OK)
        # проверка обновления транзакции
        transaction_id = url.removeprefix('/api/transaction/').removesuffix('/')
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(transaction.amount, 1000.00)

    def test_transaction_delete(self):
        """Test the deletion of a transaction by a superuser."""
        # удаление транзакции суперпользователем
        self.api_client.force_authenticate(
            user=self.superuser, token=self.superuser_token,
        )
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/',
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, config.CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')

        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, config.NO_CONTENT)
        # проверка удаления транзакции
        id = url.removeprefix('/api/transaction/').removesuffix('/')
        self.assertFalse(Transaction.objects.filter(id=id).exists())

    def test_transaction_creation_regular_user(self):
        """Test the creation of a transaction by a regular user."""
        # создание транзакции обычным пользователем инициализатором
        self.api_client.force_authenticate(
            user=self.user, token=self.user_token,
        )
        self.new_user_instance = Client.objects.create(
            user=self.user,
            first_name='Test1',
            last_name='Testovich1',
            phone='+79000000001',
        )

        body = {
            'initializer': f'/api/client/{self.new_user_instance.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/',
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, config.CREATED)
        # проверка создания транзакции
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, config.OK)

        # создание транзакции обычным пользователем не инициализатором
        self.other_user = User.objects.create_user(
            username='other_user', password='other_user',
        )
        self.other_user_token = Token.objects.create(user=self.other_user)
        self.api_client.force_authenticate(
            user=self.other_user, token=self.other_user_token,
        )
        self.other_user_instance = Client.objects.create(
            user=self.other_user,
            first_name='Test1',
            last_name='Testovich1',
            phone='+79000000001',
        )
        body = {
            'initializer': f'/api/client/{self.new_user_instance.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/',
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, config.FORBIDDEN)
