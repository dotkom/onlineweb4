from unittest.mock import MagicMock, patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser

from .models import Order, OrderLine, Product, ProductSize


class WebshopTestMixin:
    def assertInMessages(self, message_text, response):
            messages = [str(message) for message in response.context['messages']]
            self.assertIn(message_text, messages)


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


class WebshopProductDetail(TestCase, WebshopTestMixin):
    url = reverse('webshop_product', kwargs={'slug': 'product1'})

    def setUp(self):
        self.user = G(OnlineUser, username='test', ntnu_username='test')
        self.product = G(Product, name='Product 1', slug='product1', active=True, stock=12, deadline=None)

    def test_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 2,
        })

        self.assertRedirects(response, reverse('webshop_checkout'))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 2)

    def test_order_twice(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 1,
        })
        response = self.client.post(self.url, {
            'quantity': 2,
        })

        self.assertRedirects(response, reverse('webshop_checkout'))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 3)

    def test_order_not_logged_in(self):
        response = self.client.post(self.url, {
            'quantity': 1,
        })

        self.assertRedirects(response, '{}?next={}'.format(reverse('auth_login'), self.url))

    def test_order_deadline_reached(self):
        self.product.deadline = '2010-12-12 00:00Z'
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 1,
        })

        self.assertInMessages('Dette produktet er ikke lenger tilgjengelig.', response)

    def test_order_out_of_stock(self):
        self.product.stock = 0
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 1,
        })

        self.assertInMessages('Dette produktet er utsolgt.', response)

    def test_order_not_enough_stock(self):
        self.product.stock = 5
        self.product.save()
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 7,
        })

        self.assertInMessages('Det er ikke nok produkter på lageret.', response)

    def test_order_size(self):
        size = G(ProductSize, product=self.product, size='M', stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 2,
            'size': size.pk
        })

        self.assertRedirects(response, reverse('webshop_checkout'))
        order_line = OrderLine.objects.get(user=self.user)
        order = order_line.orders.get(product=self.product)
        self.assertEqual(order.quantity, 2)

    def test_order_unknown_size(self):
        size = G(ProductSize, product=self.product, size='M', stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 2,
            'size': size.pk + 1
        })

        self.assertInMessages('Vennligst oppgi et gyldig antall', response)

    def test_order_size_not_enough_stock(self):
        size = G(ProductSize, product=self.product, size='M', stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 6,
            'size': size.pk
        })

        self.assertInMessages('Det er ikke nok produkter på lageret.', response)

    def test_order_size_out_of_stock(self):
        size = G(ProductSize, product=self.product, size='M', stock=5)
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': 6,
            'size': size.pk
        })

        self.assertInMessages('Det er ikke nok produkter på lageret.', response)

    def test_order_negative_quantity(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'quantity': -1,
        })

        self.assertInMessages('Vennligst oppgi et gyldig antall', response)


class CheckoutTest(TestCase, WebshopTestMixin):
    url = reverse('webshop_pay')

    def setUp(self):
            self.user = G(OnlineUser, username='test', ntnu_username='test')

    def test_remove_inactive_order(self):
        self.client.force_login(self.user)

        order_line = G(OrderLine, user=self.user, paid=False)
        product = G(Product, active=True, stock=None, deadline=None)
        order = G(Order, order_line=order_line, product=product)

        order.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertEqual(order, Order.objects.get(pk=order.pk))

        product.active = False
        product.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_remove_sold_out_oreder(self):
        self.client.force_login(self.user)

        order_line = G(OrderLine, user=self.user, paid=False)
        product = G(Product, active=True, stock=10, deadline=None)
        order = G(Order, order_line=order_line, product=product)

        order.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertEqual(order, Order.objects.get(pk=order.pk))

        product.stock = 0
        product.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_remove_expired_oreder(self):
        self.client.force_login(self.user)

        order_line = G(OrderLine, user=self.user, paid=False)
        product = G(Product, active=True, stock=None, deadline='2100-12-12 00:00Z')
        order = G(Order, order_line=order_line, product=product)

        order.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertEqual(order, Order.objects.get(pk=order.pk))

        product.deadline = '2010-12-12 00:00Z'
        product.save()

        self.client.get(reverse("webshop_checkout"))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    @patch('apps.payment.views.stripe.Charge.create')
    def test_pay_size(self, stripe_create):
        stripe_create.return_value = MagicMock(id=123)
        self.client.force_login(self.user)
        product = G(Product, slug='product1', active=True, stock=None, deadline=None, price=50)
        size = G(ProductSize, size='L', produc=product, stock=2)
        self.client.post(reverse('webshop_product', kwargs={'slug': 'product1'}), {
            'quantity': 2,
            'size': size.pk
        })
        order_line = OrderLine.objects.get(user=self.user)

        response = self.client.post(self.url, {
            'stripeToken': 'stripy',
            'amount': 10000,
            'order_line_id': order_line.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, 'Betaling utført.'.encode())
        order_line.refresh_from_db()
        self.assertEqual(order_line.stripe_id, '123')
        size.refresh_from_db()
        self.assertEqual(size.stock, 0)

    @patch('apps.payment.views.stripe.Charge.create')
    def test_pay(self, stripe_create):
        stripe_create.return_value = MagicMock(id=123)
        self.client.force_login(self.user)
        product = G(Product, slug='product1', active=True, stock=5, deadline=None, price=50)
        self.client.post(reverse('webshop_product', kwargs={'slug': 'product1'}), {
            'quantity': 4,
        })
        order_line = OrderLine.objects.get(user=self.user)

        response = self.client.post(self.url, {
            'stripeToken': 'stripy',
            'amount': 20000,
            'order_line_id': order_line.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, 'Betaling utført.'.encode())
        order_line.refresh_from_db()
        self.assertEqual(order_line.stripe_id, '123')
        product.refresh_from_db()
        self.assertEqual(product.stock, 1)

    @patch('apps.payment.views.stripe.Charge.create')
    def test_not_enough_stock(self, stripe_create):
        self.client.force_login(self.user)
        product = G(Product, slug='product1', active=True, stock=5, deadline=None, price=50)
        order_line = G(OrderLine, user=self.user)
        G(Order, order_line=order_line, quantity=6, product=product, size=None)

        response = self.client.post(self.url, {
            'stripeToken': 'stripy',
            'amount': 30000,
            'order_line_id': order_line.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, 'Ordren er ikke gyldig.'.encode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        product.refresh_from_db()
        self.assertEqual(product.stock, 5)

    @patch('apps.payment.views.stripe.Charge.create')
    def test_wrong_subtotal(self, stripe_create):
        self.client.force_login(self.user)
        product = G(Product, slug='product1', active=True, stock=5, deadline=None, price=50)
        order_line = G(OrderLine, user=self.user)
        G(Order, order_line=order_line, quantity=4, product=product, size=None)

        response = self.client.post(self.url, {
            'stripeToken': 'stripy',
            'amount': 20001,
            'order_line_id': order_line.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, 'Invalid input'.encode())
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        product.refresh_from_db()
        self.assertEqual(product.stock, 5)

    @patch('apps.payment.views.stripe.Charge.create')
    def test_size_not_enough_stock(self, stripe_create):
        self.client.force_login(self.user)
        # product.stock should not be used
        product = G(Product, slug='product1', active=True, stock=10, deadline=None, price=50)
        size = G(ProductSize, product=product, size='M', stock=3)
        G(ProductSize, product=product, size='L', stock=5)
        order_line = G(OrderLine, user=self.user)
        G(Order, order_line=order_line, quantity=4, product=product, size=size)

        response = self.client.post(self.url, {
            'stripeToken': 'stripy',
            'amount': 20000,
            'order_line_id': order_line.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, 'Ordren er ikke gyldig.'.encode())
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        product.refresh_from_db()
        self.assertEqual(size.stock, 3)
