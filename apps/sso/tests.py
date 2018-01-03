from django.urls import reverse
from django_dynamic_fixture import G
from oauth2_provider.models import get_access_token_model, get_application_model

from apps.authentication.models import Email, OnlineUser
from apps.oauth2_provider.test import OAuth2TestCase

from .endpoints import SCOPES

Application = get_application_model()
AccessToken = get_access_token_model()


class UserinfoTestCase(OAuth2TestCase):
    scopes = SCOPES

    def setUp(self):
        self.user = G(OnlineUser)
        G(Email, user=self.user)
        self.access_token = self.generate_access_token(self.user)

    def test_get_userinfo(self):
        url = reverse('sso_user')
        resp = self.client.get(url, **self.generate_headers())

        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.username, resp.json().get('username'))
