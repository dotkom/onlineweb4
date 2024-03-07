from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventory.models import Item


class ShopItemTestCase(APITestCase):
    basename = "shop_inventory"

    def get_list_url(self):
        return reverse(f"{self.basename}-list")

    def get_detail_url(self, _id):
        return reverse(f"{self.basename}-detail", args=(_id,))

    def test_item_list_empty(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_list_exists(self):
        G(Item, available=True)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_item_detail(self):
        item = G(Item, available=True)

        response = self.client.get(self.get_detail_url(item.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
