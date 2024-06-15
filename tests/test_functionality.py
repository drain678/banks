from django.utils import timezone
from decimal import Decimal
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client as TestClient, TestCase
from django.urls import reverse

from banks_app.models import Bank, BankAccount, Client, Transaction


def extract_data_from_response(response, keys_to_find):
    soup = BeautifulSoup(response.content, 'html.parser')
    extracted_data = {}

    for key in keys_to_find:
        found_value = None

        for tag in soup.find_all('p'):
            strong_tag = tag.find('strong')
            if strong_tag and strong_tag.text.strip() == key:
                found_value = tag.get_text(strip=True).replace(key, '').strip()
                break

        extracted_data[key] = found_value

    return extracted_data


class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.bank = Bank.objects.create(title='Test Bank', foundation_date='2023-01-01')
        self.client_user = Client.objects.create(user=self.user, first_name='Test', last_name='User', phone='+70000000000')
        self.bank_account = BankAccount.objects.create(balance=1000, bank=self.bank, client=self.client_user)
        self.client.login(username='testuser', password='12345')

    def test_profile_view(self): 
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/profile.html')

        extracted_data = extract_data_from_response(response, ['First Name:', 'Last Name:', 'Phone:', 'Username:'])
        self.assertEqual(extracted_data['First Name:'], 'Test')
        self.assertEqual(extracted_data['Last Name:'], 'User')
        self.assertEqual(extracted_data['Username:'], 'testuser')
        self.assertEqual(extracted_data['Phone:'], '+70000000000')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('homepage'))

    def test_clients_view(self): 
        response = self.client.get(reverse('clients'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/clients.html')

        extracted_data = extract_data_from_response(response, ['First Name:', 'Last Name:', 'Phone:', 'Username:'])
        self.assertEqual(extracted_data['First Name:'], 'Test')
        self.assertEqual(extracted_data['Last Name:'], 'User')
        self.assertEqual(extracted_data['Username:'], 'testuser')
        self.assertEqual(extracted_data['Phone:'], '+70000000000')


    def test_create_client_view_post(self): 
        self.client.logout()
        new_user = User.objects.create_user(username='newuser', password='12345')
        self.client.login(username='newuser', password='12345')
        response = self.client.post(reverse('create_client'), {
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+70000000001',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(user=new_user).exists())

    def test_register_view(self):
        self.client.logout()
        response = self.client.post(reverse('register'), {
            'username': 'newuser2',
            'password1': '12345password',
            'password2': '12345password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser2').exists())

    def test_delete_transaction_view(self):  
        self.client.logout()
        self.new_user = User.objects.create_user(username='newuser', password='12345', is_superuser=True)
        self.client_user2 = Client.objects.create(user=self.new_user, first_name='Test', last_name='User', phone='+70000000000')
        self.client.login(username='newuser', password='12345')
        transaction = Transaction.objects.create(
            initializer=self.client_user2,
            amount=100,
            transaction_date='2023-01-01',
            from_bank_account_id=self.bank_account,
            to_bank_account_id=self.bank_account
        )
        response = self.client.get(reverse('delete_transaction', args=[transaction.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_confirm_transaction_view(self):  
        response = self.client.get(reverse('confirm_transaction'))
        self.assertEqual(response.status_code, 302)

    def test_create_transaction_view_get(self):
        response = self.client.get(reverse('create_transaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/create_transaction.html')

    def test_create_transaction_view_post(self):  
        self.new_user = User.objects.create_user(
            username='newuser', password='12345', is_superuser=True)
        self.client_user2 = Client.objects.create(
            user=self.new_user, first_name='Test', last_name='User', phone='+70000000000')
        self.to_bank_account = BankAccount.objects.create(
            balance=500, bank=self.bank, client=self.client_user2)
        response = self.client.post(reverse('create_transaction'), {
            'from_bank_account_id': self.bank_account.id,
            'to_bank_account_uuid': self.to_bank_account.id,
        }
        )
        response = self.client.post(reverse('confirm_transaction'), {
            'transaction_date': timezone.now().date(),
            'description': 'Test transaction',
            'amount': '100.0',
        })
        self.assertEqual(response.status_code, 302)

        self.assertEqual(BankAccount.objects.get(
            pk=self.bank_account.id).balance, Decimal('900.0'))
        self.assertEqual(BankAccount.objects.get(
            pk=self.to_bank_account.id).balance, Decimal('600.0'))


    def test_user_transaction_list_view(self):
        response = self.client.get(reverse('user_transactions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/user_transactions.html')

    def test_transaction_detail_view(self): 
        transaction = Transaction.objects.create(
            initializer=self.client_user,
            amount=100,
            transaction_date='2023-01-01',
            from_bank_account_id=self.bank_account,
            to_bank_account_id=self.bank_account
        )
        response = self.client.get(reverse('transaction_detail', args=[transaction.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/transaction_detail.html')

    def test_transactions_view(self): 
        response = self.client.get(reverse('transactions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/transactions.html')

    def test_bank_accounts_view(self): 
        response = self.client.get(reverse('bank_accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/bank_accounts.html')

    def test_create_bank_account_view(self): 
        response = self.client.post(reverse('create_bank_account'), {
            'balance': 500,
            'bank': self.bank.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BankAccount.objects.filter(
            client=self.client_user, bank=self.bank).exists())

    def test_delete_bank_account_view(self):
        response = self.client.get(reverse('delete_bank_account', args=[self.bank_account.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BankAccount.objects.filter(pk=self.bank_account.pk).exists())

    def test_homepage_view(self): 
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_create_bank_view(self): 
        self.new_user = User.objects.create_user(
            username='newuser', password='12345', is_superuser=True)
        self.client_user2 = Client.objects.create(user=self.new_user, first_name='Test', last_name='User', phone='+70000000000')
        self.client.login(username='newuser', password='12345')
        response = self.client.post(reverse('create_bank'), {
            'title': 'New Bank',
            'foundation_date': '2023-01-01',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bank.objects.filter(title='New Bank').exists())

    def test_delete_bank_view(self): 
        self.new_user = User.objects.create_user(
            username='newuser', password='12345', is_superuser=True)
        self.client_user2 = Client.objects.create(user=self.new_user, first_name='Test', last_name='User', phone='+70000000000')
        self.client.login(username='newuser', password='12345')
        response = self.client.get(reverse('delete_bank', args=[self.bank.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Bank.objects.filter(pk=self.bank.pk).exists())

    def test_bank_list_view(self): 
        response = self.client.get(reverse('banks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/banks.html')

    def test_bank_detail_view(self): 
        response = self.client.get(reverse('bank_detail', args=[self.bank.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/bank_detail.html')

    def test_client_detail_view(self):  
        response = self.client.get(reverse('client_detail', args=[self.client_user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/client_detail.html')
