from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django_dynamic_fixture import G

from apps.authentication.models import OnlineUser

from ..models import TYPE_CHOICES
from .utils import (add_to_arrkom, add_to_bedkom, add_to_committee, add_to_fagkom, add_to_trikom,
                    generate_event)

EVENTS_ADMIN_LIST_URL = reverse_lazy('admin:events_event_changelist')
EVENTS_DASHBOARD_INDEX_URL = reverse_lazy('dashboard_events_index')


def event_admin(event):
    return reverse('admin:events_event_change', args=(event.id,))


def attendance_list(event):
    return reverse('event_attendees_pdf', args=(event.id,))


def event_dashboard(event):
    return reverse('dashboard_events_edit', args=(event.id,))


class EventAdminTestCase(TestCase):
    def setUp(self):
        self.user = G(OnlineUser)
        self.client.force_login(self.user)

        self.event = generate_event(TYPE_CHOICES[0][0])

        # General committee members should not be able to access event admin pages.
        self.expected_resp_code_own_django = 302
        self.expected_resp_code_own_dashboard = 403

    def test_view_event_list_admin(self):
        resp = self.client.get(EVENTS_ADMIN_LIST_URL)

        self.assertEqual(self.expected_resp_code_own_django, resp.status_code)

    def test_view_event_detail_admin(self):
        resp = self.client.get(event_admin(self.event))

        self.assertEqual(self.expected_resp_code_own_django, resp.status_code)

    def test_view_event_attendance_list(self):
        resp = self.client.get(attendance_list(self.event))

        self.assertEqual(self.expected_resp_code_own_django, resp.status_code)

    def test_view_event_list_dashboard(self):
        resp = self.client.get(EVENTS_DASHBOARD_INDEX_URL)

        self.assertEqual(self.expected_resp_code_own_dashboard, resp.status_code)

    def test_view_event_detail_dashboard(self):
        resp = self.client.get(event_dashboard(self.event))

        self.assertEqual(self.expected_resp_code_own_dashboard, resp.status_code)


class ArrkomEventAdminTestCase(EventAdminTestCase):
    def setUp(self):
        super().setUp()
        self.event = generate_event(TYPE_CHOICES[0][0])

        add_to_arrkom(self.user)

        self.expected_resp_code_own_django = 200
        self.expected_resp_code_own_dashboard = 200


class BedkomEventAdminTestCase(EventAdminTestCase):
    def setUp(self):
        super().setUp()
        self.event = generate_event(TYPE_CHOICES[1][0])

        add_to_bedkom(self.user)

        self.expected_resp_code_own_django = 200
        self.expected_resp_code_own_dashboard = 200


class FagkomEventAdminTestCase(EventAdminTestCase):
    def setUp(self):
        super().setUp()
        self.event = generate_event(TYPE_CHOICES[2][0])

        add_to_fagkom(self.user)

        self.expected_resp_code_own_django = 200
        self.expected_resp_code_own_dashboard = 200


class TrikomEventAdminTestCase(EventAdminTestCase):
    def setUp(self):
        super().setUp()
        self.event = generate_event(TYPE_CHOICES[0][0])

        add_to_trikom(self.user)

        self.expected_resp_code_own_django = 200
        self.expected_resp_code_own_dashboard = 200

    def test_view_event_attendance_list(self):
        pass  # Trikom doesn't have access to any attendance lists per now.
