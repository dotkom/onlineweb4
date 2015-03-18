# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.events.dashboard.views',
    url(r'^$', 'index', name='dashboard_events_index'),
    url(r'^past$', 'past', name='dashboard_events_past'),

    url(r'^create/$', 'create_event', name='dashboard_event_create'),
    # details views
    url(r'^(?P<event_id>\d+)/$', 'event_details', name='dashboard_event_details'),
    # url endpoints for saving forms
    url(r'^(?P<event_id>\d+)/attendance/$', 'event_change_attendance', name='dashboard_event_change_attendance'),
    url(r'^(?P<event_id>\d+)/attendees/$', 'event_change_attendees', name='dashboard_event_change_attendees'),
    url(r'^(?P<event_id>\d+)/reservation/$', 'event_change_reservation', name='dashboard_event_change_reservation'),
    # catch-all for other tabs
    url(r'^(?P<event_id>\d+)/(?P<active_tab>\w+)/$', 'event_details', name='dashboard_event_details_active'),


    url(r'^attendee/(?P<attendee_id>\d+)/$', 'attendee_details', name='dashboard_attendee_details'),
)
