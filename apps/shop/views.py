# API v1
import django_filters

from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.ext.rest_framework import TokenHasScope

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import OnlineUser as User
from apps.inventory.models import Item
from apps.payment.models import PaymentTransaction
from apps.shop.models import OrderLine
from apps.shop.serializers import OrderLineSerializer, UserSerializer, TransactionSerializer
from apps.shop.serializers import ItemSerializer


class OrderLineViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

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
    authentication_classes = [OAuth2Authentication,]
    permission_classes = [TokenHasScope,]
    required_scopes = ['shop.readwrite',]
    filter_fields = ('rfid',)


class InventoryViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Item.objects.filter(available=True)
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)

