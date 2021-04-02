import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from oauth2_provider.views.base import AuthorizationView as DefaultAuthorizationView

from apps.sso.serializers import (
    Oauth2ClientReadOwnSerializer,
    Oauth2AccessReadOwnSerializer,
    Oauth2RefreshTokenSerializer,
    Oauth2GrantSerializer,
    Oauth2ApplicationConsentSerializer,
)
from rest_framework import viewsets, permissions
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_refresh_token_model,
    get_grant_model,
)
from apps.sso.models import ApplicationConsent

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


class Oauth2ClientViewSet(viewsets.ModelViewSet):
    serializer_class = Oauth2ClientReadOwnSerializer
    queryset = get_application_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]


class Oauth2AccessViewSet(viewsets.ModelViewSet):
    """
    An `Access Token` is issued on successfull login and grants access to our API endpoints.
    """

    serializer_class = Oauth2AccessReadOwnSerializer
    queryset = get_access_token_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]


class Oauth2RefreshTokenViewSet(viewsets.ModelViewSet):
    """
    A `Refresh Token` is an issued token which can be used 
    for generating new access tokens without asking the user to consent again.
    """

    serializer_class = Oauth2RefreshTokenSerializer
    queryset = get_refresh_token_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]


class Oauth2GrantViewSet(viewsets.ModelViewSet):
    """
    A `Grant` represents a login attempt, where "application" is the client which was tried to log into.
    """

    serializer_class = Oauth2GrantSerializer
    queryset = get_grant_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]


class Oauth2ConsentViewSet(viewsets.ModelViewSet):
    serializer_class = Oauth2ApplicationConsentSerializer
    queryset = ApplicationConsent.objects.all()
    permission_classes = [permissions.IsAuthenticated]
