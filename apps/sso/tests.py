from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from oauth2_provider.models import get_access_token_model, get_application_model

from apps.authentication.models import Email, OnlineUser

from .endpoints import SCOPES

Application = get_application_model()
AccessToken = get_access_token_model()


class UserinfoTestCase(TestCase):
    def setUp(self):
        self.user = G(OnlineUser)
        G(Email, user=self.user)
        self.application = Application.objects.create(
            name='test_client', user=self.user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            scopes=' '.join(SCOPES),
            redirect_uris='http://localhost',
        )
        self.access_token = AccessToken.objects.create(
            user=self.user, token='1234567890',
            application=self.application, scope=' '.join(SCOPES),
            expires=timezone.now() + timedelta(days=1)
        )
        self.headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + self.access_token.token,
        }

    def test_get_userinfo(self):
        url = reverse('sso_user')
        resp = self.client.get(url, **self.headers)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.username, resp.json().get('username'))
