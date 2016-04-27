from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventory.models import Item


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
