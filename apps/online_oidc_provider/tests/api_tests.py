from django.urls import reverse
from django_dynamic_fixture import G
from oidc_provider.models import (
    CLIENT_TYPE_CHOICES,
    RESPONSE_TYPE_CHOICES,
    Client,
    ResponseType,
    UserConsent,
)
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.events.tests.utils import generate_user
from apps.online_oidc_provider.test import OIDCTestCase


class ResponseTypesTest(OIDCTestCase):

    @staticmethod
    def create_response_types():
        for value, description in RESPONSE_TYPE_CHOICES:
            ResponseType.objects.create(value=value, description=description)

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('oidc_response_types-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        self.create_response_types()
        self.response_type = ResponseType.objects.all().first()

    def test_response_types_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_response_type_by_id(self):
        response = self.client.get(self.id_url(self.response_type.id), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.response_type.id)


class ClientsTest(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('oidc_clients-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        self.response_type = ResponseType.objects.all().first()
        self.oidc_client = G(Client)
        self.oidc_client.response_types.add(self.response_type)

    def test_clients_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_client_type_by_id_without_authentication(self):
        response = self.client.get(self.id_url(self.oidc_client.id), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.oidc_client.id)

    def test_user_can_create_a_client(self):
        client_data = {
            'client_type': CLIENT_TYPE_CHOICES[1],
            'redirect_uris': 'http://localhost',
            'response_types': [self.response_type.id],
        }
        response = self.client.post(self.url, data=client_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anonymous_user_cannot_create_a_client(self):
        client_data = {
            'client_type': CLIENT_TYPE_CHOICES[1],
            'redirect_uris': 'http://localhost',
            'response_types': [self.response_type.id],
        }
        response = self.client.post(self.url, data=client_data, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_their_own_client(self):
        client: Client = G(Client, owner=self.user)

        response = self.client.delete(self.id_url(client.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_other_peoples_clients(self):
        other_user: User = G(User)
        client: Client = G(Client, owner=other_user)

        response = self.client.delete(self.id_url(client.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_users_cannot_delete_un_owned_clients(self):
        client: Client = G(Client, owner=None)

        response = self.client.delete(self.id_url(client.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_un_authenticated_users_cannot_delete_un_owned_clients(self):
        client: Client = G(Client, owner=None)

        response = self.client.delete(self.id_url(client.id), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_update_client(self):
        client_name = 'test_client'
        client_name_other = 'other_name'
        client: Client = G(Client, owner=self.user, name=client_name)

        response = self.client.patch(self.id_url(client.id), data={
            'name': client_name_other,
        }, **self.headers)

        client.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('name'), client_name_other)
        self.assertEqual(client.name, client_name_other)


class UserConsentTest(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('oidc_user_consent-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        self.response_type: ResponseType = ResponseType.objects.all().first()
        self.oidc_client = G(Client)
        self.oidc_client.response_types.add(self.response_type)
        self.user_consent: UserConsent = G(UserConsent, user=self.user)

    def test_user_consent_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_consent_by_id(self):
        response = self.client.get(self.id_url(self.user_consent.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.user_consent.id)

    def test_user_cannot_get_other_users_consent(self):
        user = G(User)
        other_consent: UserConsent = G(UserConsent, user=user)
        response = self.client.get(self.id_url(other_consent.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_consent(self):
        response = self.client.delete(self.id_url(self.user_consent.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_other_users_consent(self):
        user = G(User)
        other_consent: UserConsent = G(UserConsent, user=user)
        response = self.client.delete(self.id_url(other_consent.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
