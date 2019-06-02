from datetime import date, timedelta

from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.events.tests.utils import generate_user
from apps.oidc_provider.test import OIDCTestCase


class EmailTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('user_emails-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        self.email: Email = self.user.get_email()
        self.other_email: Email = self.other_user.get_email()

    def test_emails_view_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_emails(self):
        response = self.client.get(self.id_url(self.email.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.email.id)

    def test_user_cannot_view_other_users_emails(self):
        response = self.client.get(self.id_url(self.other_email.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_create_an_email(self):
        response = self.client.post(self.url, {
            'email': 'test@example.com',
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.json().get('id'), [email.id for email in self.user.get_emails()])

    def test_user_cannot_create_an_email_with_an_existing_address(self):
        address = 'test@example.com'
        first_response = self.client.post(self.url, {
            'email': address,
        }, **self.headers)

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        second_response = self.client.post(self.url, {
            'email': address,
        }, **self.headers)

        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            second_response.json().get('email'),
            ['Det eksisterer allerede en bruker med denne e-postadressen'],
        )

    def test_user_can_change_primary_email(self):
        self.assertTrue(self.email.primary)

        email: Email = G(Email, user=self.user, verfied=False)

        response = self.client.patch(self.id_url(email.id), {
            'primary': True,
        }, **self.headers)

        self.email.refresh_from_db()
        email.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(email.primary)
        """ Make sure the other email is not primary anymore """
        self.assertFalse(self.email.primary)

    def test_user_cannot_remove_primary_email_without_selecting_a_new_primary(self):
        self.assertTrue(self.email.primary)

        email: Email = G(Email, user=self.user, verfied=False)

        response = self.client.patch(self.id_url(email.id), {
            'primary': False,
        }, **self.headers)

        self.email.refresh_from_db()
        email.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('primary'),
            ['Kan bare endre primærepost ved å sette en annen som primær']
        )
        self.assertFalse(email.primary)
        """ Make sure the other email is still primary """
        self.assertTrue(self.email.primary)

    def test_user_cannot_verify_emails_without_token(self):
        email: Email = G(Email, user=self.user, verfied=False)
        response = self.client.patch(self.id_url(email.id), {
            'verified': True,
        }, **self.headers)

        email.refresh_from_db()

        self.assertFalse(response.json().get('verified'))
        self.assertFalse(email.verified)

    def test_user_cannot_change_the_address_of_an_existing_email(self):
        address = 'test@example.com'
        other_address = 'test@test.io'
        email: Email = G(Email, user=self.user, verfied=False, email=address)
        self.client.patch(self.id_url(email.id), {
            'email': other_address,
        }, **self.headers)

        email.refresh_from_db()

        self.assertEqual(email.email, address)
        self.assertNotEqual(email.email, other_address)


class PositionsTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('user_positions-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        self.period_start = date(2017, 3, 1)
        self.period_end = self.period_start + timedelta(days=366)
        self.position: Position = G(Position, user=self.user)
        self.other_position: Position = G(
            Position,
            user=self.other_user,
            period_start=self.period_start,
            period_end=self.period_end,
        )
        self.position_data = {
            'position': 'medlem',
            'period_start': str(self.period_start),
            'period_end': str(self.period_end),
            'committee': 'hs',
        }

    def test_positions_view_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_positions(self):
        response = self.client.get(self.id_url(self.position.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.position.id)

    def test_user_cannot_view_other_users_positions(self):
        response = self.client.get(self.id_url(self.other_position.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_create_a_position(self):
        response = self.client.post(self.url, self.position_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('position'), self.position_data.get('position'))

    def test_user_can_only_create_positions_for_themselves(self):
        response = self.client.post(self.url, {
            **self.position_data,
            'user': self.other_user.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_positions_with_start_after_end(self):
        date_before_period_start = self.period_start - timedelta(days=1)

        response = self.client.post(self.url, {
            **self.position_data,
            'period_end': str(date_before_period_start),
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('non_field_errors'),
            ['Vervets starttid kan ikke være etter vervets sluttid']
        )

    def test_user_cannot_create_positions_with_start_at_same_time_as_end(self):
        response = self.client.post(self.url, {
            **self.position_data,
            'period_end': str(self.period_start),
            'period_start': str(self.period_start),
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('non_field_errors'),
            ['Du kan ikke starte og avslutte et verv på samme dag']
        )

    def test_user_can_update_a_position(self):
        new_period_end = str(self.period_end + timedelta(days=365))

        response = self.client.patch(self.id_url(self.position.id), {
            'period_start': str(self.period_start),  # Both are currently required to make a change
            'period_end': new_period_end,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('period_end'), new_period_end)

    def test_user_can_delete_a_position(self):
        response = self.client.delete(self.id_url(self.position.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.position, self.user.positions.all())

    def test_user_cannot_delete_other_users_positions(self):
        other_position = self.other_position
        response = self.client.delete(self.id_url(self.other_position.id), **self.headers)
        other_position.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.other_position, other_position)


class SpecialPositionsTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('user_special_positions-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.special_position: SpecialPosition = G(SpecialPosition, user=self.user)
        self.other_special_position: SpecialPosition = G(SpecialPosition, user=self.other_user)

    def test_special_positions_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_special_positions(self):
        response = self.client.get(self.id_url(self.special_position.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.special_position.id)

    def test_user_cannot_view_other_users_special_positions(self):
        response = self.client.get(self.id_url(self.other_special_position.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
