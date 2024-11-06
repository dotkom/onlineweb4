from datetime import timedelta

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Event
from apps.feedback.models import Feedback, FeedbackRelation, TextQuestion


def create_generic_attendance_event():
    event_start = timezone.now() + timezone.timedelta(days=1)
    event_end = event_start + timezone.timedelta(days=1)
    event = G(Event, event_start=event_start, event_end=event_end)
    G(AttendanceEvent, event=event, max_capacity=2)
    return event


def add_permissions(user):
    user.is_staff = True
    user.save()
    user.user_permissions.add(
        Permission.objects.filter(codename="view_event").first(),
        Permission.objects.filter(codename="add_event").first(),
        Permission.objects.filter(codename="delete_feedbackrelation").first(),
    )


class DashboardEventsURLTestCase(TestCase):
    def setUp(self):
        self.user = G(User)
        self.client.force_login(self.user)

    def test_dashboard_events_index_missing_permissions(self):
        url = reverse("dashboard_events_index")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_events_index_empty(self):
        add_permissions(self.user)
        url = reverse("dashboard_events_index")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_index_exists(self):
        create_generic_attendance_event()
        add_permissions(self.user)
        url = reverse("dashboard_events_index")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_events_create(self):
        add_permissions(self.user)
        url = reverse("dashboard_event_create")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_remove_feedback_from_event(self):
        # self.committee = G(Group, name="Arrkom")
        add_permissions(self.user)

        event = create_generic_attendance_event()
        # event = G(Event, event_type=EventType.BEDPRES, organizer=self.committee)
        # G(AttendanceEvent, event=event)

        feedback = Feedback.objects.create(author=self.user)
        TextQuestion.objects.create(feedback=feedback)
        deadline = timezone.now().date() + timedelta(days=4)

        feedbackrelation = FeedbackRelation.objects.create(
            feedback=feedback, content_object=event, deadline=deadline, active=True
        )

        assign_perm("delete_feedbackrelation", self.user, feedbackrelation)
        # self.user.groups.add(self.committee)
        self.assertTrue(self.user.has_perm("feedback.delete_feedbackrelation"))

        url = reverse(
            "dashboard_events_remove_feedback",
            kwargs={"event_id": event.id, "pk": feedback.id},
        )
        response = self.client.get(url)

        """
        django.template.exceptions.TemplateDoesNotExist: feedback/feedbackrelation_confirm_delete.html
        """

        self.assertEqual(response.status_code, status.HTTP_200_OK)
