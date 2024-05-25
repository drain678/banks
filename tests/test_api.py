import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone

from banks_app.models import Bank, Client, BankAccount, Transaction

class BanksAPITest(TestCase): 
        def setUp(self): 
            self.api_client = APIClient() 
                        # users
            self.user = User.objects.create_user(username='user', password='user')
            # self.user.save() 
            self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
            # self.superuser.save() 
            # tokens for users
            self.user_token = Token.objects.create(user=self.user)
            self.superuser_token = Token.objects.create(user=self.superuser)

        def test_bank_403(self): 
            self.api_client.force_authenticate(user=self.user, token=self.user_token)
            response = self.api_client.post('/api/bank/', {'title': 'Test'})
            self.assertEqual(response.status_code, 403) 

        def test_bank_creation_duplicate_title(self): 
            Bank.objects.create(title='Hello')
            self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
            body = {'title': 'Hello'}
            response = self.api_client.post('/api/bank/', body)
            self.assertEqual(response.status_code, 400)

        def test_bank_creation(self): 
            self.api_client.force_authenticate(user=self.superuser, token=self.superuser_token)
            TEST_TITLE = 'Sigma'
            body = {'title': TEST_TITLE} 
            response = self.api_client.post('/api/bank/', body)
            self.assertEqual(response.status_code, 201) 
            resp_body = json.loads(response.content.decode())
            url = resp_body['url'].removeprefix('http://testserver')
            id = url.removeprefix('/api/bank/').removesuffix('/')
            # print(response.content) 
            response = self.api_client.get(url)
            self.assertEqual(response.status_code, 200) 
            resp_body = json.loads(response.content.decode())
            self.assertEqual(resp_body['title'], TEST_TITLE) 

            # client = Client.objects.filter(id=id).first() 
            # self.assertEqual(client.user, self.superuser) 
            # print(bank) 

            response = self.api_client.get('/api/bank/')
            self.assertEqual(response.status_code, 200)
            resp_body = json.loads(response.content.decode())
            for b in resp_body:  # TODO: use django test framework method for testing lists 
                 if b['title'] == TEST_TITLE: 
                    return  
            raise Exception(f'bank was not found in /api/bank/, response: {resp_body}')



# def create_api_test(model_class, url, creation_attrs):
#     class ApiTest(TestCase):
#         def setUp(self):
#             self.client = APIClient()
#             # users
#             self.user = User.objects.create_user(username='user', password='user')
#             self.superuser = User.objects.create_superuser(username='admin', password='admin', is_superuser=True)
#             # tokens for users
#             self.user_token = Token.objects.create(user=self.user)
#             self.superuser_token = Token.objects.create(user=self.superuser)

#         def api_methods(
#                 self, user: User, token: Token,
#                 post_exp: int, put_exp: int, delete_exp: int,
#         ):
#             self.client.force_authenticate(user=user, token=token)

#             # create model object
#             self.created_id = model_class.objects.create(**creation_attrs).id

#             instance_url = f'{url}{self.created_id}/'
#             print(instance_url)
#             # GET all
#             self.assertEqual(self.client.get(
#                 url).status_code, status.HTTP_200_OK)

#             # # HEAD all
#             # self.assertEqual(self.client.head(
#             #     url).status_code, status.HTTP_200_OK)

#             # # OPTIONS all
#             # self.assertEqual(self.client.get(
#             #     url).status_code, status.HTTP_200_OK)

#             # GET instance
#             self.assertEqual(self.client.get(
#                 instance_url).status_code, status.HTTP_200_OK)

#             # # OPTIONS instance
#             # self.assertEqual(self.client.get(
#             #     instance_url).status_code, status.HTTP_200_OK)

#             # POST
#             self.assertEqual(self.client.post(
#                 url, creation_attrs).status_code, post_exp)

#             # PUT
#             self.assertEqual(self.client.put(
#                 instance_url, creation_attrs).status_code, put_exp)

#             # DELETE
#             self.assertEqual(self.client.delete(
#                 instance_url).status_code, delete_exp)

#         def test_superuser(self):
#             self.api_methods(
#                 self.superuser, self.superuser_token,
#                 status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
#             )

#         # def test_user(self):
#         #     self.api_methods(
#         #         self.user, self.user_token,
#         #         status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN
#         #     )

#     return ApiTest


# BankApiTest = create_api_test(
#     Bank, '/api/bank/', {'title': 'Russia'}
# )
# BankAccountApiTest = create_api_test(BankAccount, '/api/bank_account/', {'balance': 100.0, 'client': Client})
# ClientApiTest = create_api_test(Client, '/api/client/', {'user': User, 'first_name': 'Katya', 'last_name': 'Meow', 'phone': +79195138803})
#TransactionApiTest = create_api_test(
#     Transaction, '/api/transaction/',
#     {'initializer': Client, 'amount': 200.0, 'transaction_date': timezone.now().date(),
#     'description': 'obed', 'from_bank_account_id': BankAccount, 'to_bank_account_id': BankAccount}
#  )