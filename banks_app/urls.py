from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token

from . import views

router = DefaultRouter()
router.register('bank', views.BankViewSet)
router.register('bank_account', views.BankAccountViewSet)
router.register('client', views.ClientViewSet)
router.register('transaction', views.TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    # path('token/', obtain_auth_token),
]
