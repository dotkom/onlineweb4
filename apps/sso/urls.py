# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.sso import endpoints, views

app_name = "sso"

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^user/", endpoints.oauth2_provider_userinfo, name="user"),
    url(
        r"^o/authorize/$",
        views.AuthorizationView.as_view(),
        name="oauth2_provider_authorize",
    ),
    url(r"^o/token/$", views.TokenView.as_view(), name="oauth2_provider_token"),
    url(
        r"^o/revoke/$",
        views.RevokeTokenView.as_view(),
        name="oauth2_provider_revoke_token",
    ),
]
