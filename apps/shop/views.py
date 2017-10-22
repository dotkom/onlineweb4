# API v1
from django.contrib import auth
from oauth2_provider.ext.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Email
from apps.inventory.models import Item
from apps.payment.models import PaymentTransaction
from apps.shop.models import OrderLine
from apps.shop.serializers import (ItemSerializer, OrderLineSerializer, TransactionSerializer,
                                   UserSerializer)


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
    queryset = Item.objects.filter(available=True).order_by('pk')
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SetRFIDView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['shop.readwrite']

    def post(self, request):
        username = request.data.get("username", '').lower()
        password = request.data.get("password", '')

        if not username:
            return Response('Missing authentication details', status=status.HTTP_400_BAD_REQUEST)

        if '@' in username:
            email = Email.objects.filter(email=username)
            if email:
                username = email[0].user.username

        user = auth.authenticate(username=username, password=password)

        rfid = request.data.get("rfid", '')

        if not rfid:
            return Response('Missing RFID from request payload', status=status.HTTP_400_BAD_REQUEST)

        if user and rfid:
            if user.rfid == rfid:
                return Response("OK", status=status.HTTP_200_OK)

            user.rfid = rfid
            user.save()
            return Response("OK", status=status.HTTP_200_OK)

        return Response("Invalid user credentials", status=status.HTTP_409_CONFLICT)
