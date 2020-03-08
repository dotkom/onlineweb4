from oidc_provider.lib.utils.oauth2 import extract_access_token
from oidc_provider.models import Token
from rest_framework import authentication, exceptions
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation

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

        return oauth2_token.user, None

class TokenHasScope(BasePermission):
    """
    The request is authenticated and the token used has the right scope
    """

    def has_permission(self, request, view):

        try:
            token = Token.objects.get(access_token=extract_access_token(request))  # The Token object retrieved from access_token

            if token.has_expired():
                self.message = {
                    "detail": PermissionDenied.default_detail,
                    "error": 'Token has expired',
                }
                return False

        except Token.DoesNotExist:
            self.message = {
                "detail": PermissionDenied.default_detail,
                "error": "No token provided or token does not exist",
            }

            return False

        if hasattr(token, "scope"):
            required_scopes = self.get_scopes(request, view)

            if set(required_scopes).issubset(set(token.scope)):
                return True                

            # Provide information about required scope
            self.message = {
                "detail": PermissionDenied.default_detail,
                "error": "Permission denied, required_scopes: " + str(list(required_scopes)),
            }

            return False

        return False

    def get_scopes(self, request, view):
        try:
            return getattr(view, "required_scopes")
        except AttributeError:
            raise ImproperlyConfigured(
                "TokenHasScope requires the view to define the required_scopes attribute"
            )