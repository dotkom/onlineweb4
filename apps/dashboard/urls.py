# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.dashboard.views',
    url(r'^$', 'index', name='dashboard_index'),
)
