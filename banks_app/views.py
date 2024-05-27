from rest_framework import viewsets
from .models import Bank, BankClient, Client, BankAccount, Transaction
from .serializers import BankClientSerializer, BankSerializer, ClientSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework import status
from rest_framework.response import Response


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
            id_sender = self.request.user.client.id
            if str(id_sender) == str(initializer_id):
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
