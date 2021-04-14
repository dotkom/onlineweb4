from django.conf.urls import url, include
from apps.sso import endpoints, views
from apps.api.utils import SharedAPIRootRouter

app_name = "sso"

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^user/", endpoints.oauth2_provider_userinfo, name="user"),
    url(
        r"^authorize/",
        views.AuthorizationView.as_view(),
        name="oauth2_provider_authorize",
    ),
    url(r"^", include("oauth2_provider.urls", "oauth2_provider")),
]


router = SharedAPIRootRouter()
router.register(
    "sso/admin/clients", views.Oauth2ClientAdminViewSet, basename="sso_admin-clients"
)
router.register("sso/clients", views.Oauth2ClientViewSet, basename="sso_clients")
router.register("sso/access", views.Oauth2AccessViewSet, basename="sso_access")
router.register(
    "sso/refresh-tokens", views.Oauth2RefreshTokenViewSet, basename="sso_refresh-tokens"
)
router.register("sso/grants", views.Oauth2GrantViewSet, basename="sso_grants")
router.register("sso/consents", views.Oauth2ConsentViewSet, basename="sso_consents")
