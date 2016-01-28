# API v1
from django.contrib import auth

from apps.authentication.models import OnlineUser as User, Email
from apps.inventory.models import Item
from apps.payment.models import PaymentTransaction
from apps.shop.models import OrderLine
from apps.shop.serializers import OrderLineSerializer, UserSerializer, TransactionSerializer
from apps.shop.serializers import ItemSerializer

from oauth2_provider.ext.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class OrderLineViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['shop.readwrite']

    def create(self, request):
        serializer = OrderLineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


class TransactionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = PaymentTransaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['shop.readwrite']

    def create(self, request):
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['shop.readwrite']
    filter_fields = ('rfid',)


class InventoryViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Item.objects.filter(available=True)
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)


class SetRFIDView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['shop.readwrite']

    def post(self, request, format=None):
        username = request.data["username"].lower()
        password = request.data["password"]

        if '@' in username:
            email = Email.objects.filter(email=username)
            if email:
                username = email[0].user.username

        user = auth.authenticate(username=username, password=password)

        if user:
            user.rfid = request.data["rfid"]
            user.save()
            return Response("OK", status=status.HTTP_200_OK)

        return Response("Invalid user credentials", status=status.HTTP_409_CONFLICT)
