# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    'apps.sso.views',
    url(r'^$', 'index', name='sso_index'),
    url(r'^o/authorize/$', views.AuthorizationView.as_view(), name='oauth2_provider_authorize'),
    url(r'^o/token/$', views.TokenView.as_view(), name='oauth2_provider_token'),
    url(r'^o/revoke/$', views.RevokeTokenView.as_view(), name='oauth2_provider_revoke_token'),
)
