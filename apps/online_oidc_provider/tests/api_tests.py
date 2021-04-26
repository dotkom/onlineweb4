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
from apps.online_oidc_provider.serializers import ClientReadOwnSerializer
from apps.online_oidc_provider.test import OIDCTestCase


class ResponseTypesTest(OIDCTestCase):
    @staticmethod
    def create_response_types():
        for value, description in RESPONSE_TYPE_CHOICES:
            ResponseType.objects.create(value=value, description=description)

    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("oidc_response_types-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"

        self.create_response_types()
        self.response_type = ResponseType.objects.all().first()

    def test_response_types_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_response_type_by_id(self):
        response = self.client.get(
            self.id_url(self.response_type.id), **self.bare_headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.response_type.id)


class ClientsTest(OIDCTestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("oidc_clients-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"

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
        response = self.client.get(
            self.id_url(self.oidc_client.id), **self.bare_headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.oidc_client.id)

    def test_user_can_create_a_client(self):
        client_data = {
            "client_type": CLIENT_TYPE_CHOICES[1][0],
            "redirect_uris": ["http://localhost"],
            "response_types": [self.response_type.id],
        }
        response = self.client.post(self.url, data=client_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anonymous_user_cannot_create_a_client(self):
        client_data = {
            "client_type": CLIENT_TYPE_CHOICES[1][0],
            "redirect_uris": "http://localhost",
            "response_types": [self.response_type.id],
        }
        response = self.client.post(self.url, data=client_data, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_update_client(self):
        client_name = "test_client"
        client_name_other = "other_name"
        client: Client = G(Client, owner=self.user, name=client_name)

        response = self.client.patch(
            self.id_url(client.id), data={"name": client_name_other}, **self.headers
        )

        client.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), client_name_other)
        self.assertEqual(client.name, client_name_other)

    def test_secret_is_set_on_creation_if_confidential(self):
        client_data = {
            "name": "test_secret",
            "client_type": CLIENT_TYPE_CHOICES[0][0],
            "redirect_uris": ["http://localhost:3000"],
            "response_types": [self.response_type.id],
        }

        response = self.client.post(self.url, data=client_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("name"), client_data["name"])
        self.assertIsNotNone(response.json().get("client_secret"))
        self.assertIsNot(response.json().get("client_secret"), "")

    def test_secret_is_removed_on_public_clients(self):
        client_name = "test_secret_removal"
        client = G(
            Client,
            name=client_name,
            owner=self.user,
            client_type=CLIENT_TYPE_CHOICES[0][0],
        )

        self.assertIsNotNone(client.client_secret)
        response = self.client.patch(
            self.id_url(client.id),
            data={"client_type": CLIENT_TYPE_CHOICES[1][0]},
            **self.headers
        )
        self.assertEqual(response.json().get("client_secret"), "")

    def test_secret_is_not_leaked(self):
        response = self.client.get(self.url, **self.bare_headers)
        clients = response.json()["results"]
        for client in clients:
            self.assertIsNone(client.get("client_secret", None))

    def test_get_own_only_allows_https(self):
        response = self.client.post(reverse("oidc_clients-get-own"), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_own_gets_only_own(self):
        other_user = G(User)
        client = G(Client, name="test", owner=self.user)
        client_with_other_owner = G(
            Client, name="test_should_not_be_shown", owner=other_user
        )
        response = self.client.post(
            reverse("oidc_clients-get-own"), **self.headers, secure=True
        )
        clients = response.json()["results"]
        serialized_client = ClientReadOwnSerializer(instance=client)
        self.assertEqual(clients, [serialized_client.data])
        self.assertNotIn(client_with_other_owner, clients)


class UserConsentTest(OIDCTestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("oidc_user_consent-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"

        self.response_type: ResponseType = ResponseType.objects.all().first()
        self.oidc_client = G(Client)
        self.oidc_client.response_types.add(self.response_type)
        self.user_consent: UserConsent = G(UserConsent, user=self.user)

    def test_user_consent_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_consent_by_id(self):
        response = self.client.get(self.id_url(self.user_consent.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.user_consent.id)

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
