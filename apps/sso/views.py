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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.sso.models import ApplicationConsent
from apps.sso.permissions import TokenHasScopeOrSuperUser
from apps.sso.serializers import (
    SSOAccessReadOwnSerializer,
    SSOApplicationConsentSerializer,
    SSOClientConfidentialSerializer,
    SSOClientNonSensitiveSerializer,
    SSOGrantSerializer,
    SSORefreshTokenSerializer,
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


class SSOClientPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Basic information regarding our clients are considered public information.
    """

    serializer_class = SSOClientNonSensitiveSerializer
    queryset = get_application_model().objects.all()


class SSOClientOwnViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Methods for editing own clients, does not require any scopes, but only the owner can edit.
    Non-sensitive, but personal.
    """

    serializer_class = SSOClientNonSensitiveSerializer

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


class SSOClientConfidentialViewSet(viewsets.ModelViewSet):
    """
    These endpoints are reserved for the `authentication:admin`-scopes which is given per-request basis.
    They are intended for apps able to transmit sensitive information only.
    """

    serializer_class = SSOClientConfidentialSerializer
    permission_classes = [IsAuthenticated, TokenHasScopeOrSuperUser]
    required_scopes = ["authentication:admin"]

    def get_queryset(self):
        user = self.request.user
        return get_application_model().objects.filter(user=user)


class SSOAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    An `Access Token` is issued on successfull login and grants access to our API endpoints.
    """

    serializer_class = SSOAccessReadOwnSerializer
    queryset = get_access_token_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return get_access_token_model().objects.filter(user=request.user)


class SSORefreshTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A `Refresh Token` is an issued token which can be used
    for generating new access tokens without asking the user to consent again.
    """

    serializer_class = SSORefreshTokenSerializer
    queryset = get_refresh_token_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return get_refresh_token_model().objects.filter(user=request.user)


class SSOGrantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A `Grant` represents a login attempt, where "application" is the client which was tried to log into.
    """

    serializer_class = SSOGrantSerializer
    queryset = get_grant_model().objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        queryset = get_grant_model().objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SSOConsentViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = SSOApplicationConsentSerializer
    queryset = ApplicationConsent.objects.all()
    permission_classes = [TokenHasScopeOrSuperUser]

    @action(detail=False, methods=["GET"])
    def get_own(self, request):
        return ApplicationConsent.objects.filter(user=request.user)
