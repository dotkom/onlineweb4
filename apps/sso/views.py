import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_refresh_token_model,
)
from oauth2_provider.views.base import AuthorizationView as DefaultAuthorizationView
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.rest_framework.mixins import MultiSerializerMixin
from apps.sso.models import ApplicationConsent
from apps.sso.permissions import TokenHasScopeOrSuperUser
from apps.sso.serializers import (
    Oauth2AccessReadOwnSerializer,
    Oauth2ApplicationConsentSerializer,
    Oauth2ClientNonSensitiveSerializer,
    Oauth2ClientSerializer,
    Oauth2GrantSerializer,
    Oauth2RefreshTokenSerializer,
)

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


class Oauth2ClientPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Basic information regarding our clients are considered public information.
    """

    serializer_class = Oauth2ClientNonSensitiveSerializer
    queryset = get_application_model().objects.all()


class Oauth2ClientOwnViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Methods for editing own clients, does not require any scopes, but only the owner can edit.
    """

    serializer_class = Oauth2ClientNonSensitiveSerializer

    def get_queryset(self):
        user = self.request.user
        return get_application_model().objects.filter(user=user)

    @action(detail=True, methods=["DELETE"])
    def revoke(self, request, pk=None):
        access_tokens = get_access_token_model().objects.filter(application=pk)
        refresh_tokens = get_refresh_token_model().objects.filter(application=pk)
        for access_token in access_tokens:
            access_token.revoke()
        for refresh_token in refresh_tokens:
            refresh_token.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Oauth2ClientConfidentialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    These endpoints are reserved for the `authentication:admin`-scopes which is given per-request basis.
    They are intended for apps able to transmit sensitive information only.
    """

    serializer_class = Oauth2ClientSerializer
    permission_classes = [TokenHasScopeOrSuperUser]
    required_scopes = ["authentication:admin"]

    def get_queryset(self):
        user = self.request.user
        return get_application_model().objects.filter(user=user)


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
        queryset = get_grant_model().objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class Oauth2ConsentViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = Oauth2ApplicationConsentSerializer
    queryset = ApplicationConsent.objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return ApplicationConsent.objects.filter(user=request.user)
