# API v1
import logging

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.inventory.models import Item
from apps.payment.models import PaymentTransaction
from apps.shop.forms import SetRFIDForm
from apps.shop.models import MagicToken, OrderLine
from apps.shop.serializers import (ItemSerializer, OrderLineSerializer, TransactionSerializer,
                                   UserSerializer, UserOrderLineSerializer)
from apps.shop.utils import create_magic_token


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

class UserOrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = UserOrderLineSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return OrderLine.objects.none()
        return OrderLine.objects.filter(user=self.request.user)


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
        request_magic_link = request.data.get('magic_link', False)
        send_magic_link_email = request.data.get('send_email', True)

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

        if not user and username and rfid and request_magic_link:
            onlineuser = None
            try:
                onlineuser = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response('User does not exist', status=status.HTTP_400_BAD_REQUEST)

            magic_token = create_magic_token(onlineuser, rfid, send_token_by_email=send_magic_link_email)
            data = {
                'token': str(magic_token.token),
                'url': '{}{}'.format(settings.BASE_URL, reverse('shop_set_rfid', args=[str(magic_token.token)]))
            }
            return Response(data=data, status=status.HTTP_201_CREATED)

        return Response("Invalid user credentials", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class SetRFIDWebView(FormView):
    form_class = SetRFIDForm
    template_name = 'shop/set_rfid.html'
    success_url = reverse_lazy('home')

    def get(self, request, token='', *args, **kwargs):
        get_object_or_404(MagicToken, token=token)
        return super().get(request, token, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['current_rfid'] = self.request.user.rfid
        kwargs['token'] = self.kwargs.get('token')
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['rfid'] = MagicToken.objects.get(token=self.kwargs.get('token')).data
        return initial

    def post(self, request, token='', *args, **kwargs):
        logger = logging.getLogger(__name__)
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)

        if not token:
            form.add_error('Det finnes ingen token i denne forespørselen.')
            return self.form_invalid(form)

        magictoken = None
        try:
            magictoken = MagicToken.objects.get(token=token)
        except MagicToken.DoesNotExist:
            form.add_error('Tokenet du prøver å bruke eksisterer ikke.')
            return self.form_invalid(form)

        old_rfid = magictoken.user.rfid
        magictoken.user.rfid = magictoken.data
        magictoken.user.save()

        logger.debug('{authed_user} updated RFID for {user} (from "{old}" to "{new}").'.format(
            authed_user=self.request.user, user=magictoken.user,
            old=old_rfid, new=magictoken.data
        ))

        magictoken.delete()

        messages.success(request, 'Oppdaterte RFID for {}'.format(magictoken.user))
        return self.form_valid(form)
