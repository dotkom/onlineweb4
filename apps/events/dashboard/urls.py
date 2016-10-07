# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.events.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='dashboard_events_index'),
    url(r'^past$', views.past, name='dashboard_events_past'),

    url(r'^create/$', views.CreateEventView.as_view(), name='dashboard_event_create'),
    # details views
    url(r'^(?P<event_id>\d+)/$', views.event_details, name='dashboard_event_details'),
    url(r'^(?P<pk>\d+)/edit/$', views.UpdateEventView.as_view(), name='dashboard_events_edit'),
    url(r'^(?P<event_id>\d+)/create/$', views.AddAttendanceView.as_view(), name='dashboard_event_create_attendance'),
    # url endpoints for saving forms
    url(r'^(?P<event_id>\d+)/attendance/$', views.event_change_attendance, name='dashboard_event_change_attendance'),
    url(r'^(?P<event_id>\d+)/attendees/$', views.event_change_attendees, name='dashboard_event_change_attendees'),
    url(r'^(?P<event_id>\d+)/reservation/$', views.event_change_reservation, name='dashboard_event_change_reservation'),
    # catch-all for other tabs
    url(r'^(?P<event_id>\d+)/(?P<active_tab>\w+)/$', views.event_details, name='dashboard_event_details_active'),


    url(r'^attendee/(?P<attendee_id>\d+)/$', views.attendee_details, name='dashboard_attendee_details'),
]
