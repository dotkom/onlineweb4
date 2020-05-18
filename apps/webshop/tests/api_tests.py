import stripe
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.events.tests.utils import generate_user
from apps.online_oidc_provider.test import OIDCTestCase
from apps.webshop.models import Order, OrderLine, Product, ProductSize


class WebshopProductTests(OIDCTestCase):
    def setUp(self):
        self.user = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("webshop_products-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"
        self.product1: Product = G(Product)

    def test_product_list_returns_ok_without_login(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_product_list(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_product_details(self):
        response = self.client.get(self.id_url(self.product1.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.product1.id)


class WebshopOrderLineTests(OIDCTestCase):
    def setUp(self):
        self.user = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("webshop_orderlines-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"
        date_next_year = timezone.now() + timezone.timedelta(days=366)
        self.mock_card = {
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": date_next_year.year,
            "cvc": "123",
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS["prokom"]
        self.payment_method = stripe.PaymentMethod.create(
            type="card", card=self.mock_card
        )

        self.product1: Product = G(
            Product,
            name="Onlinegenser",
            deadline=timezone.now() + timezone.timedelta(days=7),
        )

        self.product_size_s: ProductSize = G(ProductSize, size="S")
        self.product_size_m: ProductSize = G(ProductSize, size="M")
        self.product_size_l: ProductSize = G(ProductSize, size="L")

        self.order_line1: OrderLine = G(OrderLine, user=self.user)

    def test_unauthenticated_user_is_denied_access(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_view_order_line_list(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_their_own_order_lines(self):
        response = self.client.get(self.id_url(self.order_line1.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.order_line1.id)

    def test_user_can_create_empty_order_lines(self):
        user_order_lines = OrderLine.objects.filter(user=self.user)
        amount_of_user_order_lines = user_order_lines.count()
        # Set all order lines as paid to allow creation of new empty order line
        for line in user_order_lines:
            line.paid = True
            line.save()

        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            OrderLine.objects.filter(user=self.user).count(),
            amount_of_user_order_lines + 1,
        )

    def test_user_cannot_create_order_line_when_they_have_unpaid_order_lines(self):
        G(OrderLine, user=self.user, paid=False)
        user_order_lines = OrderLine.objects.filter(user=self.user)
        amount_of_user_order_lines = user_order_lines.count()

        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("non_field_errors"),
            [
                "Du har allerede en handlekurv som ikke er betalt, betal eller slett den for å kunne opprette en ny"
            ],
        )
        self.assertEqual(
            OrderLine.objects.filter(user=self.user).count(), amount_of_user_order_lines
        )

    def test_user_can_pay_for_an_order_line(self):
        G(Order, order_line=self.order_line1, product=self.product1)
        payment = self.order_line1.payment
        payment_price = payment.price()

        url = reverse("payment_relations-list")

        response = self.client.post(
            url,
            {
                "payment": payment.id,
                "payment_price": payment_price.id,
                "payment_method_id": self.payment_method.id,
            },
            **self.headers,
        )
        self.order_line1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.order_line1.paid, True)


class WebshopOrderTests(OIDCTestCase):
    def setUp(self):
        self.user = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("webshop_orders-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"

        self.product1: Product = G(
            Product,
            name="Onlinegenser",
            deadline=timezone.now() + timezone.timedelta(days=7),
        )

        self.product_size_s: ProductSize = G(ProductSize, size="S")
        self.product_size_m: ProductSize = G(ProductSize, size="M")
        self.product_size_l: ProductSize = G(ProductSize, size="L")

        self.get_order_line = lambda: OrderLine.get_current_order_line_for_user(
            self.user
        )
        self.order: Order = G(Order, order_line=self.get_order_line().id)

    def test_unauthenticated_user_is_denied_access(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_view_order_list(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_their_own_orders(self):
        response = self.client.get(self.id_url(self.order.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.order.id)

    def test_user_can_create_orders(self):
        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_order_without_data(self):
        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("product"), ["Dette feltet er påkrevd."])

    def test_user_cannot_create_order_without_a_product(self):
        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("product"), ["Dette feltet er påkrevd."])

    def test_user_can_create_an_order_with_a_size(self):
        product_size_l: ProductSize = G(ProductSize, size="L", product=self.product1)

        response = self.client.post(
            self.url,
            {"product": self.product1.id, "size": product_size_l.id},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_an_order_with_an_unsupported_size(self):
        G(ProductSize, size="L", product=self.product1)
        unsupported_size = self.product_size_s

        response = self.client.post(
            self.url,
            {"product": self.product1.id, "size": unsupported_size.id},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("size"),
            ["Den gitte størrelsen er ikke tilgjengelig for dette produktet"],
        )

    def test_user_cannot_create_order_for_a_product_with_a_size_without_specifying_size(
        self,
    ):
        G(ProductSize, size="L", product=self.product1)

        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("size"),
            ["Dette produktet krever at du velger en størrelse"],
        )

    def test_user_cannot_create_order_with_size_for_products_without_sizes(self):

        response = self.client.post(
            self.url,
            {"product": self.product1.id, "size": self.product_size_l.id},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("size"),
            ["Du kan ikke velge en størrelse for dette produktet"],
        )

    def test_user_cannot_add_the_same_product_twice(self):
        G(Order, product=self.product1, order_line=self.get_order_line())

        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("non_field_errors"),
            ["Dette produktet er allerede i handlevognen din"],
        )

    def test_user_cannot_create_orders_with_inactive_products(self):
        self.product1.active = False
        self.product1.save()

        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("product"),
            ["Produktet er ikke lenger aktivt og kan ikke kjøpes"],
        )

    def test_user_cannot_create_orders_with_products_past_their_deadline(self):
        self.product1.deadline = timezone.now() - timezone.timedelta(days=7)
        self.product1.save()

        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("product"),
            ["Tidsfristen for å kjøpe produktet har utgått"],
        )

    def test_user_cannot_add_products_with_not_enough_stock(self):
        self.product1.stock = 0
        self.product1.save()

        response = self.client.post(
            self.url, {"product": self.product1.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("product"),
            ["Det er ikke flere varer igjen av produktet"],
        )

    def test_user_cannot_create_order_with_product_with_not_enough_stock_of_selected_size(
        self,
    ):
        self.product1.stock = 10
        self.product1.save()

        self.product_size_s.product = self.product1
        self.product_size_s.stock = 10
        self.product_size_s.save()
        self.product_size_m.product = self.product1
        self.product_size_m.stock = 0
        self.product_size_m.save()

        response = self.client.post(
            self.url,
            {"product": self.product1.id, "size": self.product_size_m.id},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("size"),
            [f"Det er ikke flere varer igjen av dette produktet in denne størrelsen"],
        )
