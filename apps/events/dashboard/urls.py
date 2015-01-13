# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.events.dashboard.views',
    url(r'^$', 'index', name='dashboard_event_index'),
    url(r'^(?P<event_id>\d+)/$', 'details', name='dashboard_event_details'),
    url(r'^attendee/(?P<attendee_id>\d+)/$', 'attendee_details', name='dashboard_attendee_details'),
)
