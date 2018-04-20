from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status

from .models import Product


class WebshopHome(TestCase):
    url = reverse('webshop_home')

    def test_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_active_products_in_context(self):
        G(Product, name="Product 1", active=True)
        G(Product, name="Product 2", active=False)
        G(Product, name="Product 3", active=True)

        response = self.client.get(self.url)

        self.assertEqual(len(response.context['products']), 2)
