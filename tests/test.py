from decimal import Decimal
import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from config import CLIENT_BUSIK, CLIENT_STESHA, METOD_NOT_ALLOWED, FORBIDDEN, BAD_REQUEST, OK, CREATED, NO_CONTENT, TEST_TITLE

from banks_app.models import Bank, Client, BankAccount, Transaction

# class BanksAPITest(TestCase): 
#         def setUp(self):
#             self.api_client = APIClient() 
#             # users
#             self.user = User.objects.create_user(username='user', password='user')
#             self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
#             # tokens for users
#             self.user_token = Token.objects.create(user=self.user)
#             self.superuser_token = Token.objects.create(user=self.superuser)
        
#         def test_bank_creation(self):
#             # проверка статус кода на создание банка
#             self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#             body = {'title': TEST_TITLE}
#             response = self.api_client.post('/api/bank/', body)
#             self.assertEqual(response.status_code, CREATED)

#             # проверка на то, что банк действительно создался
#             resp_body = json.loads(response.content.decode())
#             url = resp_body['url'].removeprefix('http://testserver')
#             id = url.removeprefix('/api/bank/').removesuffix('/')
#             response = self.api_client.get(url)
#             self.assertEqual(response.status_code, OK)

#             # проверка получения банка обычного пользователя
#             self.api_client.force_authenticate(user=self.user, token=self.user_token)
#             response = self.api_client.get(url)
#             self.assertEqual(response.status_code, OK)

#             # проверка заголовков
#             self.assertEqual(self.api_client.head(url).status_code, OK)

#             # проверка на то, что у банка правильное название
#             resp_body = json.loads(response.content.decode())
#             self.assertEqual(resp_body['title'], TEST_TITLE)

#             # проверка на то, что этот банк среди других банков
#             response = self.api_client.get('/api/bank/')
#             self.assertEqual(response.status_code, OK)
#             resp_body = json.loads(response.content.decode())
#             bank_titles = [b['title'] for b in resp_body]
#             self.assertIn(TEST_TITLE, bank_titles, f'bank was not found in /api/bank/, response: {resp_body}')



#         def test_bank_403(self): 
#             self.api_client.force_authenticate(user=self.user, token=self.user_token)
#             response = self.api_client.post('/api/bank/', {'title': TEST_TITLE})
#             self.assertEqual(response.status_code, FORBIDDEN) 


#         def test_bank_creation_duplicate_title(self): 
#             Bank.objects.create(title=TEST_TITLE)
#             self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#             body = {'title': TEST_TITLE}
#             response = self.api_client.post('/api/bank/', body)
#             self.assertEqual(response.status_code, BAD_REQUEST)


#         def test_bank_delete(self):
#             self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#             body = {'title': TEST_TITLE}
#             response = self.api_client.post('/api/bank/', body)
#             self.assertEqual(response.status_code, CREATED)
#             resp_body = json.loads(response.content.decode())
#             url = resp_body['url'].removeprefix('http://testserver')
#             response = self.api_client.delete(url)
#             self.assertEqual(response.status_code, NO_CONTENT)


#         def test_bank_update(self):
#             self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#             body = {'title': TEST_TITLE}
#             response = self.api_client.post('/api/bank/', body)
#             self.assertEqual(response.status_code, CREATED)
#             resp_body = json.loads(response.content.decode())
#             resp_body['title'] = 'Banka_ogurcov'
#             url = resp_body['url'].removeprefix('http://testserver')
#             response = self.api_client.put(url, resp_body)
#             self.assertEqual(response.status_code, OK)
        

# class ClientsAPITest(TestCase):
#     def setUp(self):
#         self.api_client = APIClient()
#         # users
#         self.user = User.objects.create_user(username='user', password='user')
#         self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
#         # tokens for users
#         self.user_token = Token.objects.create(user=self.user)
#         self.superuser_token = Token.objects.create(user=self.superuser)

#     def test_client_creation(self):
#         # проверка созданния супер пользователя
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = CLIENT_BUSIK
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         # проверка получения супер пользователя
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         id = url.removeprefix('/api/client/').removesuffix('/')
#         client = Client.objects.filter(id=id).first()
#         self.assertEqual(client.user, self.superuser)
#         # проверка создания обычного пользователя
#         self.api_client.force_authenticate(user=self.user, token=self.user_token)
#         body = CLIENT_STESHA
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         # проверка получения обычного пользователя
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         id = url.removeprefix('/api/client/').removesuffix('/')
#         client = Client.objects.filter(id=id).first()
#         self.assertEqual(client.user, self.user)
#         # проверка заголовков
#         self.assertEqual(self.api_client.head(url).status_code, OK)

#     def test_client_delete(self):
#         # проверка удаления от супер пользователя
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = CLIENT_BUSIK
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.delete(url)
#         self.assertEqual(response.status_code, METOD_NOT_ALLOWED)
#         # проверка удаления от обычного пользователя
#         self.api_client.force_authenticate(user=self.user, token=self.user_token)
#         body = CLIENT_STESHA
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.delete(url)
#         self.assertEqual(response.status_code, METOD_NOT_ALLOWED)

#     def test_client_update(self):
#         # проверка обновления супер пользователя
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = CLIENT_BUSIK
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         resp_body['first_name'] = 'Pusik'
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.put(url, resp_body)
#         self.assertEqual(response.status_code, OK)
#         # проверка обновления обычного пользователя
#         self.api_client.force_authenticate(user=self.user, token=self.user_token)
#         body = CLIENT_STESHA
#         response = self.api_client.post('/api/client/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         resp_body['first_name'] = 'Steshik'
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.put(url, resp_body)
#         self.assertEqual(response.status_code, OK)


# class BankAccountAPITest(TestCase):
#     def setUp(self):
#         self.api_client = APIClient()
#         # users
#         self.user = User.objects.create_user(username='user', password='user')
#         self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
#         # tokens for users
#         self.user_token = Token.objects.create(user=self.user)
#         self.superuser_token = Token.objects.create(user=self.superuser)
#         # creating bank
#         self.bank = Bank.objects.create(title=TEST_TITLE, foundation_date=timezone.now().date())
#         # creating client
#         self.client_instance = Client.objects.create(user=self.user, first_name='Test', last_name='Testovich', phone='+79000000000')
        
#     def test_bank_account_creation(self):
#         # проверка создания банковского счёта суперпользователем
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = {'balance': 1000.00, 'bank': f'/api/bank/{self.bank.id}/', 'client': f'/api/client/{self.client_instance.id}/'}
#         response = self.api_client.post('/api/bank_account/', body)
#         self.assertEqual(response.status_code, CREATED)
#         # проверка получения созданного банковского счёта суперпользователем
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.get(url)
#         self.assertEqual(response.status_code, OK)
#         # проверка на зачисление верной суммы
#         bank_account_id = url.removeprefix('/api/bank_account/').removesuffix('/')
#         bank_account = BankAccount.objects.get(id=bank_account_id)
#         self.assertEqual(bank_account.balance, 1000.00)
#         # проверка заголовков
#         self.assertEqual(self.api_client.head(url).status_code, OK)
#         # проверка получения созданного банковского счёта обычным пользователем
#         self.api_client.force_authenticate(user=self.user, token=self.user_token)
#         response = self.api_client.get(url)
#         self.assertEqual(response.status_code, OK)

#     def test_bank_account_update(self):
#         # обновленние банковского счёта суперпользователем
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = {'balance': '1000.00', 'bank': f'/api/bank/{self.bank.id}/','client': f'/api/client/{self.client_instance.id}/'}
#         response = self.api_client.post('/api/bank_account/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         resp_body['balance'] = '2000.0'
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.put(url, resp_body)
#         self.assertEqual(response.status_code, OK)
#         # проверка обновления банковского счёта
#         bank_account_id = url.removeprefix('/api/bank_account/').removesuffix('/')
#         bank_account = BankAccount.objects.get(id=bank_account_id)
#         self.assertEqual(bank_account.balance, 2000.00)

#     def test_bank_account_delete(self):
#         # удаление банковского счёта суперпользователем
#         self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
#         body = {'balance': '1000.00', 'bank': f'/api/bank/{self.bank.id}/', 'client': f'/api/client/{self.client_instance.id}/'}
#         response = self.api_client.post('/api/bank_account/', body)
#         self.assertEqual(response.status_code, CREATED)
#         resp_body = json.loads(response.content.decode())
#         url = resp_body['url'].removeprefix('http://testserver')
#         response = self.api_client.delete(url)
#         self.assertEqual(response.status_code, NO_CONTENT)
#         # проверка удаления банковского счёта
#         id = url.removeprefix('/api/bank_account/').removesuffix('/')
#         self.assertFalse(BankAccount.objects.filter(id=id).exists())

#     def test_bank_account_403(self):
#         self.api_client.force_authenticate(user=self.user, token=self.user_token)
#         body = {'balance': '1000.00', 'bank': f'/api/bank/{self.bank.id}/', 'client': f'/api/client/{self.client_instance.id}/'}
#         response = self.api_client.post('/api/bank_account/', body)
#         self.assertEqual(response.status_code, FORBIDDEN)


class TransactionAPITest(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        # users
        self.user = User.objects.create_user(username='user', password='user')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
        # tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
        # creating bank
        self.bank = Bank.objects.create(title=TEST_TITLE, foundation_date=timezone.now().date())
        # creating client
        self.client_instance_1 = Client.objects.create(user=self.superuser, first_name='Test1', last_name='Testovich1', phone='+79000000001')
        # сreating bank accounts
        self.bank_account_1 = BankAccount.objects.create(balance=Decimal('1000.00'), bank=self.bank, client=self.client_instance_1)
        self.bank_account_2 = BankAccount.objects.create(balance=Decimal('2000.00'), bank=self.bank, client=self.client_instance_1)

    def test_transaction_creation(self):
        # создание транзакции для суперпользователя
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/'
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, CREATED)
        # проверка получения созданного банковского счёта суперпользователем
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, OK)
        # проверка заголовков
        self.assertEqual(self.api_client.head(url).status_code, OK)


    def test_transaction_update(self):
        # обновление транзакции суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/'
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, CREATED)
        resp_body = json.loads(response.content.decode())
        resp_body['amount'] = '1000.00'
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.put(url, resp_body)
        self.assertEqual(response.status_code, OK)
        # проверка обновления транзакции
        transaction_id = url.removeprefix('/api/transaction/').removesuffix('/')
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(transaction.amount, 1000.00)

    def test_transaction_delete(self):
        # удаление транзакции суперпользователем
        self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
        body = {
            'initializer': f'/api/client/{self.client_instance_1.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/'
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, CREATED)
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, NO_CONTENT)
        # проверка удаления транзакции
        id = url.removeprefix('/api/transaction/').removesuffix('/')
        self.assertFalse(Transaction.objects.filter(id=id).exists())

    def test_transaction_creation_regular_user(self):
        # создание транзакции обычным пользователем инициализатором
        new_user = User.objects.create_user(username='new_user', password='new_user')
        new_user_token = Token.objects.create(user=new_user)
        self.api_client.force_authenticate(user=new_user, token=new_user_token)
        self.new_user_instance = Client.objects.create(
            user=new_user, first_name='Test1', last_name='Testovich1', phone='+79000000001')

        body = {
            'initializer': f'/api/client/{self.new_user_instance.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/'
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, CREATED)
        # проверка создания транзакции
        resp_body = json.loads(response.content.decode())
        url = resp_body['url'].removeprefix('http://testserver')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, OK)

        # создание транзакции обычным пользователем не инициализатором
        self.api_client.force_authenticate(user=self.user, token=self.user_token)
        other_user = User.objects.create_user(username='other_user', password='other_user')
        other_user_token = Token.objects.create(user=other_user)
        self.user_instance = Client.objects.create(user=other_user, first_name='Test1', last_name='Testovich1', phone='+79000000001')
        body = {
            'initializer': f'/api/client/{self.user_instance.id}/',
            'amount': '500.00',
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'from_bank_account_id': f'/api/bank_account/{self.bank_account_1.id}/',
            'to_bank_account_id': f'/api/bank_account/{self.bank_account_2.id}/'
        }
        response = self.api_client.post('/api/transaction/', body)
        self.assertEqual(response.status_code, FORBIDDEN)
