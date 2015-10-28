# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.events.views',
    url(r'^$', 'index', name='events_index'),
    url(r'^(?P<event_id>\d+)/attendees/$', 'generate_pdf', name='event_attendees_pdf'),
    url(r'^(?P<event_id>\d+)/attend/$', 'attendEvent', name='attend_event'),
    url(r'^(?P<event_id>\d+)/unattend/$', 'unattendEvent', name='unattend_event'),
    url(r'^(?P<event_id>\d+)/(?P<event_slug>[a-zA-Z0-9_-]+)/$', 'details', name='events_details'),
    url(r'^search/.*$', 'search_events', name="search_events"),
    url(r'^mail-participants/(?P<event_id>\d+)$', 'mail_participants', name="event_mail_participants"),
    # iCalendar
    url(r'^events.ics$', 'calendar_export', name='events_ics'),
    url(r'^(?P<event_id>\d+).ics$', 'calendar_export', name='event_ics'),
    url(r'^user/(?P<user>[\w:-]+).ics$', 'calendar_export', name='events_personal_ics'),
)

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.events import views
router = SharedAPIRootRouter()
router.register('events', views.EventViewSet, base_name='events')
