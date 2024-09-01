from django.shortcuts import redirect
from django.urls import re_path

from apps.events import views
from apps.events.feeds import OpenedSignupsFeed

urlpatterns = [
    re_path(
        r"^$",
        lambda r: redirect("https://online.ntnu.no/events", permanent=True),
        name="events_index",
    ),
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
    re_path(
        r"^(?P<event_id>\d+)/(?P<event_slug>[a-zA-Z0-9_-]+)/$",
        lambda _r, event_id, event_slug: redirect(
            f"https://online.ntnu.no/events/${event_id}", permanent=True
        ),
        name="events_details",
    ),
    re_path(
        r"^search/.*$",
        lambda _r: redirect("https://online.ntnu.no/events", permanent=True),
        name="search_events",
    ),
    re_path(
        r"^mail-participants/(?P<event_id>\d+)$",
        views.mail_participants,
        name="event_mail_participants",
    ),
    # iCalendar
    re_path(r"^events.ics$", views.calendar_export, name="events_ics"),
    re_path(r"^(?P<event_id>\d+).ics$", views.calendar_export, name="event_ics"),
    re_path(
        r"^user/(?P<user>[\w.@+-:]+).ics$",
        views.calendar_export,
        name="events_personal_ics",
    ),
    re_path("^signup-feed/$", OpenedSignupsFeed()),
]
