from django.conf.urls import include
from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.sso import endpoints, views

app_name = "sso"

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^user/", endpoints.oauth2_provider_userinfo, name="user"),
    re_path(
        r"^authorize/",
        views.AuthorizationView.as_view(),
        name="oauth2_provider_authorize",
    ),
    re_path(r"^", include("oauth2_provider.urls", "oauth2_provider")),
]


router = SharedAPIRootRouter()
router.register("sso/public", views.SSOClientPublicViewSet, basename="sso_public")
router.register("sso/clients", views.SSOClientOwnViewSet, basename="sso_clients")
router.register(
    "sso/confidential",
    views.SSOClientConfidentialViewSet,
    basename="sso_clients_confidential",
)
router.register("sso/access", views.SSOAccessViewSet, basename="sso_access")
router.register(
    "sso/refresh-tokens", views.SSORefreshTokenViewSet, basename="sso_refresh-tokens"
)
router.register("sso/grants", views.SSOGrantViewSet, basename="sso_grants")
router.register("sso/consents", views.SSOConsentViewSet, basename="sso_consents")
