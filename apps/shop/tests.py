from typing import List

from django.core import mail
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import Email, OnlineUser
from apps.inventory.models import Item
from apps.oauth2_provider.test import OAuth2TestCase
from apps.payment.models import PaymentTransaction
from apps.payment.transaction_constants import TransactionSource
from apps.shop.models import MagicToken


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


class ShopOrderLinesTestCase(OAuth2TestCase):
    scopes = ["shop.readwrite", "read", "write"]
    basename = "shop_order_lines"

    def setUp(self):
        super().setUp()
        self.user = G(OnlineUser)
        G(Email, user=self.user, primary=True)
        self.access_token = self.generate_access_token(self.user)

    def get_list_url(self):
        return reverse(f"{self.basename}-list")

    def get_detail_url(self, _id):
        return reverse(f"{self.basename}-detail", args=(_id,))

    def _add_saldo_to_user(self, amount: int):
        return G(
            PaymentTransaction,
            user=self.user,
            amount=amount,
            source=TransactionSource.CASH,
        )

    def _perform_purchase(self, order_data: List[dict]):
        data = {"user": self.user.id, "orders": order_data}
        return self.client.post(
            self.get_list_url(), data=data, **self.generate_headers()
        )

    def test_insufficient_funds(self):
        item: Item = G(Item, available=True, price=100)
        response = self._perform_purchase([{"object_id": item.id, "quantity": 1}])

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(response.json().get("detail"), "Insufficient funds")

    def test_purchase_order_line(self):
        item: Item = G(Item, available=True, price=100)
        self._add_saldo_to_user(item.price)

        response = self._perform_purchase([{"object_id": item.id, "quantity": 1}])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_purchase_not_available(self):
        item: Item = G(Item, available=False, price=100)
        self._add_saldo_to_user(item.price)

        response = self._perform_purchase([{"object_id": item.id, "quantity": 1}])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_saldo_corresponds_with_purchase_amount(self):
        item: Item = G(Item, available=True, price=100)
        self._add_saldo_to_user(item.price)
        self.assertEqual(self.user.saldo, item.price)

        self._perform_purchase([{"object_id": item.id, "quantity": 1}])

        self.assertEqual(self.user.saldo, 0)

    def test_purchase_requires_an_item_quantity(self):
        item: Item = G(Item, available=True, price=100)
        self._add_saldo_to_user(item.price)

        response = self._perform_purchase([{"object_id": item.id}])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_purchase_quantity(self):
        quantity = 3
        item: Item = G(Item, available=True, price=100)
        self._add_saldo_to_user(item.price * quantity)

        response = self._perform_purchase(
            [{"object_id": item.id, "quantity": quantity}]
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.saldo, 0)

    def test_purchase_quantity_requires_saldo_for_all(self):
        price = 100
        quantity = 3
        item: Item = G(Item, available=True, price=price)
        self._add_saldo_to_user(price)

        response = self._perform_purchase(
            [{"object_id": item.id, "quantity": quantity}]
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(response.json().get("detail"), "Insufficient funds")

    def test_purchase_multiple_items_at_once(self):
        item1_quantity = 1
        item2_quantity = 2
        item1: Item = G(Item, available=True, price=100)
        item2: Item = G(Item, available=True, price=300)

        self._add_saldo_to_user(
            item1.price * item1_quantity + item2.price * item2_quantity
        )

        response = self._perform_purchase(
            [
                {"object_id": item1.id, "quantity": item1_quantity},
                {"object_id": item2.id, "quantity": item2_quantity},
            ]
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.saldo, 0)

    def test_purchase_triggers_receipt(self):
        item: Item = G(Item, available=True, price=100)

        self.assertEqual(len(mail.outbox), 0)
        self._add_saldo_to_user(item.price)

        self.assertEqual(len(mail.outbox), 1)

        response = self._perform_purchase([{"object_id": item.id, "quantity": 1}])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 2)


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
