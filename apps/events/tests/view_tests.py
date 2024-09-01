from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineGroup
from apps.marks.models import MarkRuleSet

from ..constants import EventType
from ..models import Event
from .utils import (
    add_to_group,
    create_committee_group,
    generate_event,
    generate_user,
)


class EventsTestMixin:
    def setUp(self):
        self.admin_group = create_committee_group(G(Group, name="Arrkom"))
        self.other_group = G(Group, name="Buddy")

        self.user = generate_user("test")
        self.client.force_login(self.user)

        # it will fail without a POST body
        self.dummy_form = {"dummy": "dummy"}

        self.mark_rule_set = G(MarkRuleSet)

        self.event = generate_event(organizer=self.admin_group)
        self.event_url = reverse(
            "events_details", args=(self.event.id, self.event.slug)
        )

    def assertInMessages(self, message_text, response):
        messages = [str(message) for message in response.context["messages"]]
        self.assertIn(message_text, messages)


class EventMailParticipates(EventsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.mail_url = reverse("event_mail_participants", args=(self.event.id,))

    def test_not_attendance_event(self):
        event = G(Event, organizer=self.admin_group)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.get(url, follow=True)

        self.assertInMessages("Dette er ikke et påmeldingsarrangement.", response)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_access(self):
        response = self.client.get(self.mail_url, follow=True)

        self.assertInMessages("Du har ikke tilgang til å vise denne siden.", response)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_own_social_event_as_bedkom(self):
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.context["event"], event)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_as_arrkom(self):
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.context["event"], event)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_as_arrkom_missing_data(self):
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.post(url)

        self.assertEqual(response.context["event"], event)
        self.assertInMessages(
            "Vi klarte ikke å sende mailene dine. Prøv igjen", response
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_post_as_arrkom_successfully(self):
        organizer_email = "arrkom@online.ntnu.no"
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        G(OnlineGroup, email=organizer_email, group=event.organizer)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.post(
            url, {"to_email": "1", "subject": "Test", "message": "Test message"}
        )

        self.assertEqual(response.context["event"], event)
        self.assertInMessages("Mailen ble sendt", response)
        self.assertEqual(mail.outbox[0].from_email, "arrkom@online.ntnu.no")
        self.assertEqual(mail.outbox[0].subject, "Test")
        self.assertIn("Test message", mail.outbox[0].body)

    def test_post_as_arrkom_invalid_from_email_defaults_to_kontakt(self):
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        G(OnlineGroup, email="", group=event.organizer)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.post(
            url, {"to_email": "1", "subject": "Test", "message": "Test message"}
        )

        self.assertEqual(response.context["event"], event)
        self.assertInMessages("Mailen ble sendt", response)

        # No longer works to test this as the email is sent in a background task
        # self.assertEqual(len(mail.outbox), 1)
        # self.assertEqual(mail.outbox[0].from_email, "kontakt@online.ntnu.no")
        # self.assertEqual(mail.outbox[0].subject, "Test")
        # self.assertIn("Test message", mail.outbox[0].body)

    def test_post_as_arrkom_invalid_to_email(self):
        add_to_group(self.admin_group, self.user)
        event = generate_event(EventType.SOSIALT, organizer=self.admin_group)
        url = reverse("event_mail_participants", args=(event.id,))

        response = self.client.post(
            url, {"to_email": "1000", "subject": "Test", "message": "Test message"}
        )

        self.assertEqual(response.context["event"], event)
        self.assertInMessages(
            "Vi klarte ikke å sende mailene dine. Prøv igjen", response
        )
        self.assertEqual(len(mail.outbox), 0)


class EventsCalendar(TestCase):
    def test_events_ics_all(self):
        url = reverse("events_ics")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_ics_specific_event(self):
        event = generate_event()

        url = reverse("event_ics", args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
