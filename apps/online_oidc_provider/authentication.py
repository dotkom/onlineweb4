from oidc_provider.lib.utils.oauth2 import extract_access_token
from oidc_provider.models import Token
from rest_framework import authentication, exceptions


class OidcOauth2Auth(authentication.BaseAuthentication):
    def authenticate(self, request):
        access_token = extract_access_token(request)

        if not access_token:
            # not this kind of auth
            return None
        oauth2_token = None
        try:
            oauth2_token = Token.objects.get(access_token=access_token)
        except Token.DoesNotExist:
            return None

        if oauth2_token.has_expired():
            raise exceptions.AuthenticationFailed("The oauth2 token has expired")

        return oauth2_token.user, None

    def authenticate_header(self, request):
        # https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
        # Should actually give a link to where one could log in
        return "Plz log in"
