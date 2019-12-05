from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import Email, OnlineUser
from apps.inventory.models import Item
from apps.oauth2_provider.test import OAuth2TestCase
from apps.shop.models import MagicToken


class ShopAPIURLTestCase(APITestCase):
    def test_item_list_empty(self):
        url = reverse("item-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_list_exists(self):
        G(Item, available=True)
        url = reverse("item-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_detail(self):
        item = G(Item, available=True)
        url = reverse("item-detail", args=(item.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopSetRFIDTestCase(OAuth2TestCase):
    scopes = ["shop.readwrite", "read", "write"]

    def setUp(self):
        super().setUp()
        self.user = G(OnlineUser)
        self.access_token = self.generate_access_token(self.user)

    def test_get_magic_link(self):
        G(Email, user=self.user)
        data = {"username": self.user.username, "rfid": "1234", "magic_link": True}
        url = reverse("set_rfid")

        token_count_pre = MagicToken.objects.count()

        response = self.client.post(url, data, **self.generate_headers())

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(token_count_pre + 1, MagicToken.objects.count())
