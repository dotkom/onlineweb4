# -*- coding: utf-8 -*-

from django.conf.urls import url
from oauth2_provider.views.base import AuthorizationView, RevokeTokenView, TokenView

from apps.sso import endpoints, views


urlpatterns = [
    url(r'^$', views.index, name='sso_index'),
    url(r'^user/', endpoints.user, name='sso_user'),
    url(r'^o/authorize/$', AuthorizationView.as_view(), name='oauth2_provider_authorize'),
    url(r'^o/token/$', TokenView.as_view(), name='oauth2_provider_token'),
    url(r'^o/revoke/$', RevokeTokenView.as_view(), name='oauth2_provider_revoke_token'),
]
