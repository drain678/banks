from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from . import views

router = DefaultRouter()
router.register('bank', views.BankViewSet)
router.register('bank_account', views.BankAccountViewSet)
router.register('client', views.ClientViewSet)
router.register('transaction', views.TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('', views.homepage, name='homepage'),
    path('banks/', views.BankListView.as_view(), name='banks'),
    path('clients/', views.clients_view, name='clients'),
    path('banks/<uuid:pk>/', views.BankDetailView.as_view(), name='bank_detail'),
    path('clients/<uuid:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_bank_account/<uuid:pk>/', views.delete_bank_account_view, name='delete_bank_account'),
    path('create_bank_account/', views.create_bank_account_view, name='create_bank_account'),
    path('bank_accounts/', views.bank_accounts_view, name='bank_accounts'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('user_transactions/', views.UserTransactionListView.as_view(), name='user_transactions'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('create_client/', views.create_client, name='create_client'),
    path('create_bank/', views.create_bank_view, name='create_bank'),
    path('delete_bank/<uuid:pk>/', views.delete_bank_view, name='delete_bank'),
    path('create_transaction/', views.create_transaction, name='create_transaction'),
    path('confirm_transaction/', views.confirm_transaction, name='confirm_transaction'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('delete_transaction/<uuid:pk>/', views.delete_transaction_view, name='delete_transaction'),
]
