import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.views.base import AuthorizationView as DefaultAuthorizationView

from apps.sso.serializers import (
    Oauth2ClientReadOwnSerializer,
    Oauth2AccessReadOwnSerializer,
    Oauth2RefreshTokenSerializer,
    Oauth2GrantSerializer,
    Oauth2ApplicationConsentSerializer,
)
from rest_framework import viewsets
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_refresh_token_model,
    get_grant_model,
)
from apps.sso.models import ApplicationConsent

from apps.sso.permissions import TokenHasScopeOrSuperUser

_log = logging.getLogger("SSO")


@login_required
def index(request):
    """
    This is the main SSO view
    """

    context = {}

    return render(request, "sso/authorize.html", context)


class AuthorizationView(DefaultAuthorizationView):
    template_name = "sso/authorize.html"


# API Views


class Oauth2ClientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = Oauth2ClientReadOwnSerializer

    @action(detail=True, methods=["DELETE"])
    def revoke(self, request, pk=None):
        access_tokens = get_access_token_model().objects.filter(application=pk)
        refresh_tokens = get_refresh_token_model().objects.filter(application=pk)
        for access_token in access_tokens:
            access_token.revoke()
        for refresh_token in refresh_tokens:
            refresh_token.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Oauth2ClientAdminViewSet(viewsets.ModelViewSet):
    """
    These endpoints require the scope `authentication:admin` that is reserved for client-administration applications.
    """

    serializer_class = Oauth2ClientReadOwnSerializer
    queryset = get_application_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]
    required_scopes = ["authentication:admin"]


class Oauth2AccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    An `Access Token` is issued on successfull login and grants access to our API endpoints.
    """

    serializer_class = Oauth2AccessReadOwnSerializer
    queryset = get_access_token_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return get_access_token_model().objects.filter(user=request.user)


class Oauth2RefreshTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A `Refresh Token` is an issued token which can be used
    for generating new access tokens without asking the user to consent again.
    """

    serializer_class = Oauth2RefreshTokenSerializer
    queryset = get_refresh_token_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return get_refresh_token_model().objects.filter(user=request.user)


class Oauth2GrantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A `Grant` represents a login attempt, where "application" is the client which was tried to log into.
    """

    serializer_class = Oauth2GrantSerializer
    queryset = get_grant_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return get_grant_model().objects.filter(user=request.user)


class Oauth2ConsentViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = Oauth2ApplicationConsentSerializer
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return ApplicationConsent.objects.filter(user=request.user)
