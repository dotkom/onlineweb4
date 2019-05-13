import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.events.tests.utils import (attend_user_to_event, generate_event, generate_user,
                                     pay_for_event)
from apps.oidc_provider.test import OIDCTestCase

from .utils import add_price_to_payment, generate_event_payment


class PaymentRelationTestCase(OIDCTestCase):

    def setUp(self):
        self.committee = G(Group, name='arrKom')
        self.user = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('payment_relations-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        date_next_year = timezone.now() + timezone.timedelta(days=366)
        self.mock_card = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123'
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS['arrkom']
        self.stripe_token = stripe.Token.create(card=self.mock_card)

        self.event = generate_event(organizer=self.committee)
        self.event.event_end = timezone.now() + timezone.timedelta(days=3)
        self.event.event_start = timezone.now() + timezone.timedelta(days=2)
        self.event.attendance_event.registration_end = timezone.now() + timezone.timedelta(days=1)
        self.event.attendance_event.unattend_deadline = timezone.now() + timezone.timedelta(days=1)
        self.event.save()
        self.event.attendance_event.save()

        self.payment = generate_event_payment(self.event)
        self.attendee = attend_user_to_event(self.event, self.user)

    def test_user_can_pay_for_an_event(self):
        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_has_access_to_view_payments(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_their_own_payments(self):
        payment_relation = pay_for_event(self.event, self.user)

        response = self.client.get(self.id_url(payment_relation.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('payment').get('id'), self.payment.id)

    def test_user_cannot_view_other_users_payments(self):
        other_user = generate_user(username='other_user')
        attend_user_to_event(self.event, other_user)
        payment_relation = pay_for_event(self.event, other_user)

        response = self.client.get(self.id_url(payment_relation.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json().get('detail'), 'Ikke funnet.')

    def test_unauthenticated_client_cannot_access_payments(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Manglende autentiseringsinformasjon.')

    def test_event_payment_fails_without_stripe_token(self):
        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('stripe_token'), ['Dette feltet er påkrevd.'])

    def test_event_payment_fails_with_fake_stripe_token(self):
        token = '--fake-token--'

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': token,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f'No such token: {token}', response.json()[0])

    def test_user_cannot_pay_for_event_with_wrong_payment_price(self):
        payment_1 = self.payment
        event_2 = generate_event(organizer=self.committee)
        payment_2 = generate_event_payment(event_2)

        response = self.client.post(self.url, {
            'payment': payment_1.id,
            'payment_price': payment_2.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('non_field_errors'),
            ['Supplied payment price is not valid for the supplied payment'],
        )

    def test_attendee_has_paid_after_paying_for_event(self):
        self.assertFalse(self.attendee.has_paid)

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.attendee.has_paid)

    def test_user_cannot_pay_for_event_if_they_are_not_attending(self):
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_can_pay_for_event_with_two_payments(self):
        second_price = add_price_to_payment(self.payment, price=1000)

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': second_price.id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_pay_for_event_twice(self):
        response_1 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_cannot_pay_for_event_twice_with_different_prices(self):
        second_price = add_price_to_payment(self.payment, price=1000)

        response_1 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': second_price.id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_can_refund_event_payment(self):
        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)
        payment_relation_id = create_response.json().get('id')

        response = self.client.delete(self.id_url(payment_relation_id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), 'Betalingen har blitt refundert.')

    def test_user_cannot_refund_after_unattend_deadline(self):
        self.event.attendance_event.unattend_deadline = timezone.now() - timezone.timedelta(hours=1)
        self.event.attendance_event.save()

        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)
        payment_relation_id = create_response.json().get('id')

        response = self.client.delete(self.id_url(payment_relation_id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('message'), 'Fristen for å melde seg av har utgått')

    def test_user_cannot_refund_after_the_event_has_started(self):
        self.event.event_start = timezone.now() - timezone.timedelta(hours=1)
        self.event.save()

        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)
        payment_relation_id = create_response.json().get('id')

        response = self.client.delete(self.id_url(payment_relation_id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('message'), 'Dette arrangementet har allerede startet.')


class PaymentTransactionTestCase(OIDCTestCase):

    def setUp(self):
        self.user = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('payment_transactions-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        date_next_year = timezone.now() + timezone.timedelta(days=366)
        self.mock_card = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123'
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS['trikom']
        self.stripe_token = stripe.Token.create(card=self.mock_card)
        self.amount = 100

    def test_user_has_access_to_view_transactions(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_clients_cannot_access_transactions(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Manglende autentiseringsinformasjon.')

    def test_user_can_create_a_transaction(self):
        response = self.client.post(self.url, {
            'amount': self.amount,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_saldo_is_updated_when_a_transaction_is_created(self):
        starting_saldo = self.user.saldo
        expected_saldo = starting_saldo + self.amount

        response = self.client.post(self.url, {
            'amount': self.amount,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.user.refresh_from_db()

        self.assertEqual(self.user.saldo, expected_saldo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_a_transaction_with_wrong_price(self):
        wrong_amount = 666

        response = self.client.post(self.url, {
            'amount': wrong_amount,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('amount'), [f'{wrong_amount} er ikke en gyldig betalingspris'])

    def test_transaction_fails_without_stripe_token(self):
        response = self.client.post(self.url, {
            'amount': self.amount,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('stripe_token'), ['Dette feltet er påkrevd.'])

    def test_event_payment_fails_with_fake_stripe_token(self):
        token = '--fake-token--'

        response = self.client.post(self.url, {
            'amount': self.amount,
            'stripe_token': token,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f'No such token: {token}', response.json()[0])


class PaymentDelayTestCase(OIDCTestCase):

    def setUp(self):
        self.user = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('payment_delays-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

    def test_user_can_access_payment_delays(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_clients_cannot_access_payment_delays(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Manglende autentiseringsinformasjon.')


class PaymentPriceTestCase(OIDCTestCase):

    def setUp(self):
        self.user = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('payment_prices-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

    def test_user_can_access_payment_prices(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_clients_cannot_access_payment_delays(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Manglende autentiseringsinformasjon.')
