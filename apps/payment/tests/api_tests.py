import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.events.tests.utils import attend_user_to_event, generate_event, generate_user
from apps.oidc_provider.test import OIDCTestCase

from .utils import generate_event_payment


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
        date_next_year = timezone.now() + timezone.timedelta(days=366)
        self.mock_card = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123'
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS['arrkom']
        self.stripe_token = stripe.Token.create(card=self.mock_card)

    def test_user_can_pay_for_an_event(self):
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_payment_fails_without_stripe_token(self):
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('stripe_token'), ['Dette feltet er påkrevd.'])

    def test_event_payment_fails_with_fake_stripe_token(self):
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)
        token = '--fake-token--'

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
            'stripe_token': token,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f'No such token: {token}', response.json()[0])

    def test_user_cannot_pay_for_event_with_wrong_payment_price(self):
        event_1 = generate_event(organizer=self.committee)
        payment_1 = generate_event_payment(event_1)
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
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)
        attendee = attend_user_to_event(event, self.user)
        self.assertFalse(attendee.has_paid)

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
            'stripe_token': self.stripe_token.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(attendee.has_paid)
