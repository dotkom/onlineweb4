from unittest import mock

import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.events.tests.utils import (attend_user_to_event, generate_event, generate_user,
                                     pay_for_event)
from apps.online_oidc_provider.test import OIDCTestCase
from apps.payment import status as payment_status
from apps.payment.models import PaymentRelation

from .utils import add_price_to_payment, generate_event_payment


class IntentAction:
    type = ''


class SuccessfulPaymentIntent:
    status = 'succeeded'
    next_action = IntentAction


def mock_payment_intent_confirm():
    """
    Patches payment intent confirmation to work server side.
    A real implementation requires user interaction, like confirming with BankID.
    """
    return mock.patch('stripe.PaymentIntent.confirm', return_value=SuccessfulPaymentIntent)


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
        self.mock_3d_secure_card = {
            'number': '4000000000003220',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123',
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS['arrkom']
        self.payment_method = stripe.PaymentMethod.create(type='card', card=self.mock_card)
        self.secure_payment_method = stripe.PaymentMethod.create(type='card', card=self.mock_3d_secure_card)

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
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock_payment_intent_confirm()
    def test_initiating_a_3d_secure_payment_results_in_a_pending_payment_relation(self, _):
        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        current_payment_status = response.json().get('status')
        payment_intent_secret = response.json().get('payment_intent_secret')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_payment_status, payment_status.PENDING)
        self.assertIsNotNone(current_payment_status, payment_intent_secret)

    @mock_payment_intent_confirm()
    def test_user_can_pay_for_event_with_3d_secure_required_card(self, _):
        initial_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        self.assertEqual(initial_response.status_code, status.HTTP_201_CREATED)

        """
        Handling a payment_intent_secret _has_ to be done on a client via Stripe.js.
        Stripe will prompt the user with a modal requiring interaction via something like BankID.
        The response has been mocked in 3D secure tests, since it cannot be done with regular unit testing.
        https://stripe.com/docs/payments/payment-intents/quickstart#handling-next-actions
        """
        transaction_id = initial_response.json().get('id')
        confirm_response = self.client.patch(self.id_url(transaction_id), {
            'payment_intent_id': '--some-fake-id--',
            # Fake id works since actual validation has been disabled by the mock_payment_intent_confirm decorator
        }, **self.headers)

        current_payment_status = confirm_response.json().get('status')

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_payment_status, payment_status.DONE)

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

    def test_event_payment_fails_without_payment_method_id(self):
        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('payment_method_id'), ['Dette feltet er påkrevd.'])

    def test_event_payment_fails_with_fake_payment_method_id(self):
        fake_payment_method_id = '--fake-token--'

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': fake_payment_method_id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f'No such payment_method: {fake_payment_method_id}', response.json()[0])

    def test_user_cannot_pay_for_event_with_wrong_payment_price(self):
        payment_1 = self.payment
        event_2 = generate_event(organizer=self.committee)
        payment_2 = generate_event_payment(event_2)

        response = self.client.post(self.url, {
            'payment': payment_1.id,
            'payment_price': payment_2.price().id,
            'payment_method_id': self.payment_method.id,
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
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.attendee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.attendee.has_paid)

    @mock_payment_intent_confirm()
    def test_attendee_has_not_paid_if_secure_payment_is_pending(self, _):
        self.assertFalse(self.attendee.has_paid)

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        self.attendee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('status'), payment_status.PENDING)
        self.assertFalse(self.attendee.has_paid)

    def test_attendee_has_paid_when_secure_payment_is_confirmed(self):
        self.assertFalse(self.attendee.has_paid)

        # Relies completely on this other test to pass, running it again to not copy the code
        self.test_user_can_pay_for_event_with_3d_secure_required_card()

        self.attendee.refresh_from_db()

        self.assertTrue(self.attendee.has_paid)
        self.assertTrue(self.attendee.paid)

    def test_user_cannot_pay_for_event_if_they_are_not_attending(self):
        event = generate_event(organizer=self.committee)
        payment = generate_event_payment(event)

        response = self.client.post(self.url, {
            'payment': payment.id,
            'payment_price': payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_can_pay_for_event_with_two_payments(self):
        second_price = add_price_to_payment(self.payment, price=1000)

        response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': second_price.id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_pay_for_event_twice(self):
        response_1 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_cannot_pay_for_event_twice_with_different_prices(self):
        second_price = add_price_to_payment(self.payment, price=1000)

        response_1 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': second_price.id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json(), ['Du har ikke tilgang til å betale for denne betalingen'])

    def test_user_can_refund_event_payment(self):
        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)
        payment_relation_id = create_response.json().get('id')

        response = self.client.delete(self.id_url(payment_relation_id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), 'Betalingen har blitt refundert.')

    def test_event_payment_is_handled_as_refunded_after_user_refunds(self):
        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)
        payment_relation_id = create_response.json().get('id')

        self.client.delete(self.id_url(payment_relation_id), **self.headers)

        payment_relation = PaymentRelation.objects.get(pk=payment_relation_id)

        self.assertEqual(payment_relation.refunded, True)
        self.assertEqual(payment_relation.status, payment_status.REMOVED)
        self.assertEqual(payment_relation.is_refundable, False)

    def test_user_can_cancel_pending_event_payment(self):
        create_response = self.client.post(self.url, {
            'payment': self.payment.id,
            'payment_price': self.payment.price().id,
            'payment_method_id': self.secure_payment_method.id,
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
            'payment_method_id': self.payment_method.id,
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
            'payment_method_id': self.payment_method.id,
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
            'number': '4000000000003055',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123'
        }
        self.mock_3d_secure_card = {
            'number': '4000000000003220',
            'exp_month': 12,
            'exp_year': date_next_year.year,
            'cvc': '123',
        }
        stripe.api_key = settings.STRIPE_PUBLIC_KEYS['trikom']
        self.payment_method = stripe.PaymentMethod.create(type='card', card=self.mock_card)
        self.secure_payment_method = stripe.PaymentMethod.create(type='card', card=self.mock_3d_secure_card)
        self.amount = 100

    def test_user_has_access_to_view_transactions(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_clients_cannot_access_transactions(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Manglende autentiseringsinformasjon.')

    def test_user_can_create_a_transaction_with_a_regular_card(self):
        response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('status'), payment_status.DONE)

    @mock_payment_intent_confirm()
    def test_initiating_a_3d_secure_transaction_results_in_a_pending_transaction(self, _):
        response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        current_payment_status = response.json().get('status')
        payment_intent_secret = response.json().get('payment_intent_secret')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_payment_status, payment_status.PENDING)
        self.assertIsNotNone(current_payment_status, payment_intent_secret)

    @mock_payment_intent_confirm()
    def test_user_can_complete_a_3d_secure_transaction(self, _):
        initial_response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        self.assertEqual(initial_response.status_code, status.HTTP_201_CREATED)

        """
        Handling a payment_intent_secret _has_ to be done on a client via Stripe.js.
        Stripe will prompt the user with a modal requiring interaction via something like BankID.
        The response has been mocked in 3D secure tests, since it cannot be done with regular unit testing.
        https://stripe.com/docs/payments/payment-intents/quickstart#handling-next-actions
        """
        transaction_id = initial_response.json().get('id')
        confirm_response = self.client.patch(self.id_url(transaction_id), {
            'payment_intent_id': '--some-fake-id--',
            # Fake id works since actual validation has been disabled by the mock_payment_intent_confirm decorator
        }, **self.headers)

        current_payment_status = confirm_response.json().get('status')

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_payment_status, payment_status.DONE)

    def test_user_saldo_is_updated_when_a_transaction_is_confirmed(self):
        starting_saldo = self.user.saldo
        expected_saldo = starting_saldo + self.amount

        # Use existing test to to the hard work, since it completely relies on the things done in it.
        self.test_user_can_complete_a_3d_secure_transaction()

        self.user.refresh_from_db()

        self.assertEqual(self.user.saldo, expected_saldo)

    def test_user_saldo_is_updated_when_a_transaction_is_done(self):
        starting_saldo = self.user.saldo
        expected_saldo = starting_saldo + self.amount

        response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.user.refresh_from_db()

        self.assertEqual(self.user.saldo, expected_saldo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock_payment_intent_confirm()
    def test_user_saldo_is_not_updated_when_a_transaction_is_pending(self, _):
        starting_saldo = self.user.saldo
        saldo_id_succeeded = starting_saldo + self.amount

        response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.secure_payment_method.id,
        }, **self.headers)

        self.user.refresh_from_db()

        self.assertEqual(self.user.saldo, starting_saldo)
        self.assertNotEqual(self.user.saldo, saldo_id_succeeded)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_a_transaction_with_wrong_price(self):
        wrong_amount = 666

        response = self.client.post(self.url, {
            'amount': wrong_amount,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('amount'), [f'{wrong_amount} er ikke en gyldig betalingspris'])

    def test_transaction_fails_without_payment_method_id(self):
        response = self.client.post(self.url, {
            'amount': self.amount,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('payment_method_id'), ['Dette feltet er påkrevd.'])

    def test_event_payment_fails_with_fake_payment_method_id(self):
        fake_payment_method_id = '--fake-token--'

        response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': fake_payment_method_id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(f'No such payment_method: {fake_payment_method_id}', response.json()[0])

    def test_user_cannot_delete_transactions(self):
        create_response = self.client.post(self.url, {
            'amount': self.amount,
            'payment_method_id': self.payment_method.id,
        }, **self.headers)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        transaction_id = create_response.json().get('id')

        delete_response = self.client.delete(self.id_url(transaction_id), **self.headers)

        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.json().get('message'), 'Du kan ikke slette eksisterende transaksjoner')


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
