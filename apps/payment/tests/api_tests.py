import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.events.tests.utils import attend_user_to_event, generate_event, generate_user
from apps.oidc_provider.test import OIDCTestCase

from .utils import add_price_to_payment, generate_event_payment


class CreateAttendeeTestCase(OIDCTestCase):

    def setUp(self):
        self.committee = G(Group, name='arrKom')
        self.user = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
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
