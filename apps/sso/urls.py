# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views, endpoints

urlpatterns = patterns(
    'apps.sso.views',
    url(r'^$', 'index', name='sso_index'),
    url(r'^user/', endpoints.user, name='sso_user'),
    url(r'^o/authorize/$', views.AuthorizationView.as_view(), name='oauth2_provider_authorize'),
    url(r'^o/token/$', views.TokenView.as_view(), name='oauth2_provider_token'),
    url(r'^o/revoke/$', views.RevokeTokenView.as_view(), name='oauth2_provider_revoke_token'),
)
