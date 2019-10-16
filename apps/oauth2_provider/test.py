import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G
from oauth2_provider.models import get_access_token_model, get_application_model

from apps.sso.settings import OAUTH2_SCOPES

Application = get_application_model()
AccessToken = get_access_token_model()
User = get_user_model()


class OAuth2TestCase(TestCase):
    """
    This is a test case for oauth2_provider.
    It creates an OAuth2 Client Application and an access token for it.
    The access token is created for the user who owns the application.
    """
    scopes = OAUTH2_SCOPES.keys()

    def generate_access_token(self, user):
        return AccessToken.objects.create(
            user=user,
            token=str(uuid.uuid4()),
            application=self.application,
            scope=self.application.scopes,
            expires=timezone.now() + timedelta(days=1)
        )

    def generate_headers(self, headers={}):
        _headers = {}
        _headers.update(headers)

        _headers.update({
            'HTTP_AUTHORIZATION': 'Bearer ' + self.access_token.token,
        })

        return _headers

    def _pre_setup(self):
        super()._pre_setup()
        self._user = G(User)
        self.application = Application.objects.create(
            name='test_client', user=self._user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            scopes=' '.join(self.scopes),
            redirect_uris='http://localhost',
        )

        self.access_token = self.generate_access_token(self._user)

        self.headers = self.generate_headers()
