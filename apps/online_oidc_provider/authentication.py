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
            raise exceptions.AuthenticationFailed("The oauth2 token is invalid")

        if oauth2_token.has_expired():
            raise exceptions.AuthenticationFailed("The oauth2 token has expired")

        print("")
        print(oauth2_token)
        return oauth2_token.user, None
