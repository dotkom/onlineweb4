from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser
from apps.webshop.models import OrderLine, Product, ProductSize


class WebshopTestMixin:
    @staticmethod
    def assert_in_messages(message_text, response):
        messages = [str(message) for message in response.context["messages"]]
        assert message_text in messages


class WebshopHome(TestCase):
    url = reverse("webshop_home")

    def test_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_active_products_in_context(self):
        G(Product, name="Product 1", active=True)
        G(Product, name="Product 2", active=False)
        G(Product, name="Product 3", active=True)

        response = self.client.get(self.url)

        self.assertEqual(len(response.context["products"]), 2)


class WebshopProductDetail(TestCase, WebshopTestMixin):
    url = reverse("webshop_product", kwargs={"slug": "product1"})

    def setUp(self):
        self.user = G(OnlineUser, username="test", ntnu_username="test")
        self.product = G(
            Product,
            name="Product 1",
            slug="product1",
            active=True,
            stock=12,
            deadline=None,
        )

    def test_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 2})

        self.assertRedirects(response, reverse("webshop_checkout"))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 2)

    def test_order_twice(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 1})
        response = self.client.post(self.url, {"quantity": 2})

        self.assertRedirects(response, reverse("webshop_checkout"))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 3)

    def test_order_not_logged_in(self):
        response = self.client.post(self.url, {"quantity": 1})

        self.assertRedirects(
            response, "{}?next={}".format(reverse("auth_login"), self.url)
        )

    def test_order_deadline_reached(self):
        self.product.deadline = "2010-12-12 00:00Z"
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 1})

        self.assert_in_messages(
            "Dette produktet er ikke lenger tilgjengelig.", response
        )

    def test_order_out_of_stock(self):
        self.product.stock = 0
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 1})

        self.assert_in_messages("Dette produktet er utsolgt.", response)

    def test_order_not_enough_stock(self):
        self.product.stock = 5
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 7})

        self.assert_in_messages("Det er ikke nok produkter på lageret.", response)

    def test_order_size(self):
        size = G(ProductSize, product=self.product, size="M", stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 2, "size": size.pk})

        self.assertRedirects(response, reverse("webshop_checkout"))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 2)

    def test_order_unknown_size(self):
        size = G(ProductSize, product=self.product, size="M", stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 2, "size": size.pk + 1})

        self.assert_in_messages("Vennligst oppgi et gyldig antall", response)

    def test_order_size_not_enough_stock(self):
        size = G(ProductSize, product=self.product, size="M", stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 6, "size": size.pk})

        self.assert_in_messages("Det er ikke nok produkter på lageret.", response)

    def test_order_size_out_of_stock(self):
        size = G(ProductSize, product=self.product, size="M", stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": 6, "size": size.pk})

        self.assert_in_messages("Det er ikke nok produkter på lageret.", response)

    def test_order_negative_quantity(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"quantity": -1})

        self.assert_in_messages("Vennligst oppgi et gyldig antall", response)
