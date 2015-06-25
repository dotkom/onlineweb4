# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.sso.dashboard.views',
    url(r'^$', 'index', name='dashboard_sso_index'),
    url(r'^new/$', 'new', name='dashboard_sso_new'),
    url(r'^app/(?P<app_pk>\d+)/$', 'application', name='dashboard_sso_application'),
)
