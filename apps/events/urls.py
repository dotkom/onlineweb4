# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.events.views',
    url(r'^$', 'index', name='events_index'),
    url(r'^(?P<event_id>\d+)/attendees/$', 'generate_pdf', name='event_attendees_pdf'),
    url(r'^(?P<event_id>\d+)/attend/$', 'attendEvent', name='attend_event'),
    url(r'^(?P<event_id>\d+)/unattend/$', 'unattendEvent', name='unattend_event'),
    url(r'^(?P<event_id>\d+)/(?P<event_slug>[a-zA-Z0-9_-]+)/$', 'details', name='events_details'), 
    url(r'^search/.*$', 'search_events', name="search_events"),
)
