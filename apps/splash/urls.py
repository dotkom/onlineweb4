# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.splash.views',
    url(r'^$', 'index', name='splash_index'),
    url(r'^events.ics$', 'calendar_export', name='splash_calendar'),
)
