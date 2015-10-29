# API v1
import django_filters
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.authentication.models import OnlineUser as User
from apps.payment.models import PaymentTransaction
from apps.shop.models import OrderLine
from apps.shop.serializers import OrderLineSerializer, UserSerializer, TransactionSerializer


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


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('rfid',)
