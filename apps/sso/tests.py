from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from oidc_provider.models import CLIENT_TYPE_CHOICES, RESPONSE_TYPE_CHOICES, Client, Token

from apps.authentication.models import Email, OnlineUser
from apps.oauth2_provider.test import OAuth2TestCase
from apps.sso.userinfo import Onlineweb4Userinfo

from .endpoints import USERINFO_SCOPES


class UserinfoTestCase(OAuth2TestCase):
    scopes = USERINFO_SCOPES

    def setUp(self):
        self.user = G(OnlineUser)
        G(Email, user=self.user)
        self.access_token = self.generate_access_token(self.user)

    def test_get_userinfo(self):
        url = reverse('sso_user')
        resp = self.client.get(url, **self.generate_headers())

        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.username, resp.json().get('username'))
        self.assertEqual(Onlineweb4Userinfo(self.user).oauth2(), resp.json())


class UserinfoOIDCTestCase(TestCase):
    def setUp(self):
        self.oidc_client = Client.objects.create(
            client_type=CLIENT_TYPE_CHOICES[1],
            client_id='123',
            response_type=RESPONSE_TYPE_CHOICES[0],
            _redirect_uris='http://localhost'
        )

    def test_get_userinfo(self):
        user = G(OnlineUser)
        G(Email, user=user)

        token = Token.objects.create(
            user=user,
            client=self.oidc_client,
            expires_at=timezone.now() + timedelta(days=1),
            _scope='openid profile',
            access_token='123',
            refresh_token='456',
            _id_token='{"sub": %s}' % user.pk,
        )

        url = reverse('oidc_provider:userinfo')

        resp = self.client.get(url, HTTP_AUTHORIZATION='Bearer ' + token.access_token)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(user.pk, resp.json().get('sub'))
        self.assertEqual(user.username, resp.json().get('preferred_username'))
        self.assertEqual(user.username, resp.json().get('nickname'))
