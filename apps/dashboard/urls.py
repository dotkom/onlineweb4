# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.dashboard.views',
    url(r'^$', 'index', name='dashboard_index'),
)
