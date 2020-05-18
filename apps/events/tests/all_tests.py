# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent, Event


class EventOrderedByRegistrationTestCase(TestCase):
    def setUp(self):
        self.FEATURED_TIMEDELTA_SETTINGS = settings
        # Override settings so that the tests will work even if we update the default delta
        self.FEATURED_TIMEDELTA_SETTINGS.OW4_SETTINGS["events"][
            "OW4_EVENTS_FEATURED_DAYS_FUTURE"
        ] = 7
        self.FEATURED_TIMEDELTA_SETTINGS.OW4_SETTINGS["events"][
            "OW4_EVENTS_FEATURED_DAYS_PAST"
        ] = 7

    def test_registration_no_push_forward(self):
        """
        Tests that an AttendanceEvent with registration date far in the future is sorted by its event end date,
        like any other event.
        """
        today = timezone.now()
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(
            Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five
        )
        G(
            AttendanceEvent,
            registration_start=month_ahead_plus_five,
            registration_end=month_ahead_plus_five,
            event=pushed_event,
        )

        expected_order = [normal_event, pushed_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)

    def test_registration_start_pushed_forward(self):
        """
        Tests that an AttendanceEvent with registration date within the "featured delta" (+/- 7 days from today)
        will be pushed ahead in the event list, thus sorted by registration start rather than event end.
        """
        today = timezone.now()
        three_days_ahead = today + datetime.timedelta(days=3)
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(
            Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five
        )
        G(
            AttendanceEvent,
            registration_start=three_days_ahead,
            registration_end=three_days_ahead,
            event=pushed_event,
        )

        expected_order = [pushed_event, normal_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)

    def test_registration_past_push_forward(self):
        """
        Tests that an AttendanceEvent with a registration date in the past, outside the "featured delta" (+/- 7 days)
        will be sorted by the event's end date.
        """
        today = timezone.now()
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        month_back = today - datetime.timedelta(days=30)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(
            Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five
        )
        G(
            AttendanceEvent,
            registration_start=month_back,
            registration_end=month_back,
            event=pushed_event,
        )

        expected_order = [normal_event, pushed_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)
