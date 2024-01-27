from django.urls import reverse
from django_dynamic_fixture import G

from apps.authentication.models import Email, OnlineUser
from apps.online_oidc_provider.test import OIDCTestCase


class UserinfoOIDCTestCase(OIDCTestCase):
    def setUp(self):
        self.user = G(OnlineUser)
        self.email = G(Email, user=self.user)
        self.token = self.generate_access_token(self.user)
        self.headers = self.generate_headers()

    def test_get_userinfo(self):
        url = reverse("oidc_provider:userinfo")

        resp = self.client.get(url, **self.headers)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.pk, resp.json().get("sub"))
        self.assertEqual(self.user.username, resp.json().get("preferred_username"))
        self.assertEqual(self.user.username, resp.json().get("nickname"))

    def test_get_ow4_info(self):
        self.token = self.generate_access_token(
            self.user,
            client_id="1234",
            refresh_token="2345",
            _scope="openid profile onlineweb4",
        )
        url = reverse("oidc_provider:userinfo")

        resp = self.client.get(url, **self.generate_headers())

        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.pk, resp.json().get("sub"))
        self.assertEqual(self.user.username, resp.json().get("preferred_username"))
        self.assertEqual(self.user.username, resp.json().get("nickname"))
