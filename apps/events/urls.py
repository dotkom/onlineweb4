# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.events import views

urlpatterns = [
    url(r"^$", views.index, name="events_index"),
    url(
        r"^(?P<event_id>\d+)/attendees/pdf$",
        views.generate_pdf,
        name="event_attendees_pdf",
    ),
    url(
        r"^(?P<event_id>\d+)/attendees/json$",
        views.generate_json,
        name="event_attendees_json",
    ),
    url(r"^(?P<event_id>\d+)/attend/$", views.attendEvent, name="attend_event"),
    url(r"^(?P<event_id>\d+)/unattend/$", views.unattendEvent, name="unattend_event"),
    url(
        r"^(?P<event_id>\d+)/show_attending/$",
        views.toggleShowAsAttending,
        name="toggleShowAsAttending",
    ),
    url(
        r"^(?P<event_id>\d+)/(?P<event_slug>[a-zA-Z0-9_-]+)/$",
        views.details,
        name="events_details",
    ),
    url(r"^search/.*$", views.search_events, name="search_events"),
    url(
        r"^mail-participants/(?P<event_id>\d+)$",
        views.mail_participants,
        name="event_mail_participants",
    ),
    # iCalendar
    url(r"^events.ics$", views.calendar_export, name="events_ics"),
    url(r"^(?P<event_id>\d+).ics$", views.calendar_export, name="event_ics"),
    url(
        r"^user/(?P<user>[\w:-]+).ics$",
        views.calendar_export,
        name="events_personal_ics",
    ),
]

# API v1
router = SharedAPIRootRouter()
router.register("events", views.EventViewSet, basename="events")
router.register("attendees", views.AttendeeViewSet, basename="attendees")
router.register(
    prefix="registration/attendance-events",
    viewset=views.RegistrationAttendaceEventViewSet,
    basename="registration_attendance_events",
)
router.register(
    prefix="registration/user-attendees",
    viewset=views.RegistrationAttendeeViewSet,
    basename="registration_attendees",
)
