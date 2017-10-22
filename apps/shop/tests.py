from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django_dynamic_fixture import G
from oauth2_provider.models import AccessToken
from oauth2_provider.tests.test_auth_backends import ApplicationModel, BaseTest
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import Email, OnlineUser
from apps.inventory.models import Item
from apps.shop.models import MagicToken
from apps.sso.models import Client


class ShopAPIURLTestCase(APITestCase):
    def test_item_list_empty(self):
        url = reverse('item-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_list_exists(self):
        G(Item, available=True)
        url = reverse('item-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_detail(self):
        item = G(Item, available=True)
        url = reverse('item-detail', args=(item.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopSetRFIDTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = G(OnlineUser)
        self.app = Client.objects.create(
                     client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
                     authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
                     user=self.user,
                     scopes='shop.readwrite read write')
        self.token = AccessToken.objects.create(
                       user=self.user, token='token', application=self.app, expires=now() + timedelta(days=1),
                       scope='shop.readwrite read write')

    def _generate_auth_token(self):
        return 'Bearer %s' % self.token.token

    def test_get_magic_link(self):
        G(Email, user=self.user)
        data = {
            'username': self.user.username,
            'rfid': '1234',
            'magic_link': True,
        }
        url = reverse('set_rfid')

        token_count_pre = MagicToken.objects.count()

        response = self.client.post(url, data, HTTP_AUTHORIZATION=self._generate_auth_token())

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(token_count_pre + 1, MagicToken.objects.count())
