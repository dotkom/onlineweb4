from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G
from oidc_provider.models import (CLIENT_TYPE_CHOICES, RESPONSE_TYPE_CHOICES, Client, ResponseType,
                                  Token)

User = get_user_model()


class OIDCTestCase(TestCase):

    @staticmethod
    def _get_response_type():
        return ResponseType.objects.create(
            value=RESPONSE_TYPE_CHOICES[1]
        )

    def generate_access_token(self, user, client_id='123', refresh_token='456', _scope='openid profile'):

        oidc_client = Client.objects.create(
            client_type=CLIENT_TYPE_CHOICES[1],
            client_id=client_id,
            _redirect_uris='http://localhost'
        )
        oidc_client.response_types.add(self.id_token_response)

        return Token.objects.create(
            user=user,
            client=oidc_client,
            expires_at=timezone.now() + timezone.timedelta(days=1),
            _scope=_scope,
            access_token=client_id,
            refresh_token=refresh_token,
            _id_token='{"sub": %s}' % user.pk,
        )

    def generate_headers(self, headers={}):
        _headers = {}
        _headers.update(headers)

        _headers.update({
            'HTTP_AUTHORIZATION': f'Bearer {self.token.access_token}',
        })

        return _headers

    def _pre_setup(self):
        super()._pre_setup()
        self.id_token_response = self._get_response_type()
        self._user = G(User)
        self.token = self.generate_access_token(self._user, client_id='999', refresh_token='888')
        self.headers = self.generate_headers()
        self.bare_headers = {
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
        }
