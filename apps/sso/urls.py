# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.sso.views',
    url(r'^$', 'index', name='sso_index'),
    url(r'^o/', include('oauth2_provider.urls'), namespace='oauth2_provider'),
)
