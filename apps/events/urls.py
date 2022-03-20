# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.events import views

urlpatterns = [
    re_path(r"^$", views.index, name="events_index"),
    re_path(
        r"^(?P<event_id>\d+)/attendees/pdf$",
        views.generate_pdf,
        name="event_attendees_pdf",
    ),
    re_path(
        r"^(?P<event_id>\d+)/attendees/json$",
        views.generate_json,
        name="event_attendees_json",
    ),
    re_path(r"^(?P<event_id>\d+)/attend/$", views.attend_event, name="attend_event"),
    re_path(
        r"^(?P<event_id>\d+)/unattend/$", views.unattend_event, name="unattend_event"
    ),
    re_path(
        r"^(?P<event_id>\d+)/show_attending/$",
        views.toggle_show_as_attending,
        name="toggle_show_as_attending",
    ),
    re_path(
        r"^(?P<event_id>\d+)/(?P<event_slug>[a-zA-Z0-9_-]+)/$",
        views.details,
        name="events_details",
    ),
    re_path(r"^search/.*$", views.search_events, name="search_events"),
    re_path(
        r"^mail-participants/(?P<event_id>\d+)$",
        views.mail_participants,
        name="event_mail_participants",
    ),
    # iCalendar
    re_path(r"^events.ics$", views.calendar_export, name="events_ics"),
    re_path(r"^(?P<event_id>\d+).ics$", views.calendar_export, name="event_ics"),
    re_path(
        r"^user/(?P<user>[\w:-]+).ics$",
        views.calendar_export,
        name="events_personal_ics",
    ),
]

# API v1
router = SharedAPIRootRouter()
router.register("events", views.EventViewSet, basename="events")
