from django.conf.urls import url, include
from oauth2_provider.views.base import RevokeTokenView, TokenView
from apps.sso import endpoints, views

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
