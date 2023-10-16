# -*- encoding: utf-8 -*-
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone as timezone
from django.utils.translation import gettext_lazy as _
from django_dynamic_fixture import G

from apps.authentication.models import Email, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Attendee, Event
from apps.feedback.models import (
    Feedback,
    FeedbackRelation,
    RatingQuestion,
    TextQuestion,
)
from apps.feedback.mommy import (
    end_date,
    generate_message,
    get_committee_email,
    set_marks,
)
from apps.marks.models import Mark


class FeedbackTestCaseMixin:
    # Feedback mail
    def setUp(self):
        self.logger = logging.getLogger()

        # Setup users
        self.user1: User = G(User, username="user1", is_active=True, is_staff=True)
        Email.objects.create(user=self.user1, email="user1@gmail.com", primary=True)
        self.user2: User = G(User, username="user2")
        Email.objects.create(user=self.user2, email="user2@gmail.com", primary=True)

        self.user1.set_password("Herpaderp123")
        self.user1.save()

    def yesterday(self):
        return timezone.now() - timedelta(days=1)

    def tomorow(self):
        return timezone.now() + timedelta(days=1)

    def create_feedback_relation(
        self,
        end_date=False,
        event_type=2,
        feedback=None,
        deadline=False,
        organizer=None,
        user=None,
    ):
        if not end_date:
            end_date = self.yesterday()

        if not deadline:
            deadline = timezone.now().date() + timedelta(days=4)

        self.event = Event.objects.create(
            title="test",
            event_start=self.yesterday(),
            event_end=end_date,
            event_type=event_type,
            author=self.user1,
            organizer=organizer,
        )

        self.attendance_event = AttendanceEvent.objects.create(
            registration_start=timezone.now(),
            unattend_deadline=timezone.now(),
            registration_end=timezone.now(),
            event=self.event,
            max_capacity=30,
        )

        if not feedback:
            feedback = Feedback.objects.create(author=self.user1)
            TextQuestion.objects.create(feedback=feedback)
            RatingQuestion.objects.create(feedback=feedback)

        Attendee.objects.create(
            event=self.attendance_event, user=self.user1, attended=True
        )
        Attendee.objects.create(
            event=self.attendance_event, user=self.user2, attended=True
        )
        if user:
            Attendee.objects.create(
                event=self.attendance_event, user=user, attended=True
            )
        return FeedbackRelation.objects.create(
            feedback=feedback, content_object=self.event, deadline=deadline, active=True
        )

    # Create a feedback relation that won't work
    def create_void_feedback_relation(self):
        feedback = Feedback.objects.create(author=self.user1)
        deadline = self.tomorow()
        return FeedbackRelation.objects.create(
            feedback=feedback, content_object=self.user1, deadline=deadline, active=True
        )


class SimpleTest(FeedbackTestCaseMixin, TestCase):
    def test_users_mail_addresses(self):
        feedback_relation = self.create_feedback_relation()

        # The below if user.id check is due to Django Guardian middleware needing an AnonymousUser, that has ID -1
        user_mails = [
            user.email
            for user in User.objects.all()
            if user.username != settings.ANONYMOUS_USER_NAME
        ]

        message = generate_message(feedback_relation, self.logger)
        self.assertEqual(set(message.attended_mails), set(user_mails))

    def test_event_not_done(self):
        feedback_relation = self.create_feedback_relation(end_date=timezone.now())
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Event not done")
        self.assertFalse(message.send)

    def test_user_answered(self):
        feedback_relation = self.create_feedback_relation()
        feedback_relation.answered.set([self.user1])
        message = generate_message(feedback_relation, self.logger)

        not_answered = [self.user2.email]
        self.assertEqual(set(message.attended_mails), set(not_answered))

    def test_everyone_answered(self):
        feedback_relation = self.create_feedback_relation()
        feedback_relation.answered.set([self.user1, self.user2])
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Everyone has answered")
        self.assertFalse(message.send)
        self.assertFalse(feedback_relation.active)

    def test_deadline_passeed(self):
        feedback_relation = self.create_feedback_relation(
            deadline=self.yesterday().date()
        )
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Deadine passed")
        self.assertFalse(feedback_relation.active)

    def test_last_warning(self):
        feedback_relation = self.create_feedback_relation(
            deadline=timezone.now().date()
        )
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Last warning")
        self.assertTrue(message.send)

    def test_warning(self):
        feedback_relation = self.create_feedback_relation(
            deadline=timezone.now().date() + timedelta(days=2)
        )
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Warning message")
        self.assertTrue(message.send)

    def test_first_mail(self):
        feedback_relation = self.create_feedback_relation()
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "First message")
        self.assertTrue(message.send)
        self.assertTrue(feedback_relation.first_mail_sent)

    def test_no_message(self):
        feedback_relation = self.create_feedback_relation(
            end_date=timezone.now() - timedelta(days=2)
        )
        feedback_relation.first_mail_sent = True
        message = generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "No message generated")
        self.assertFalse(message.send)

    def test_committee_mails(self):
        organizer_group: OnlineGroup = G(OnlineGroup, email="test@example.com")

        feedback_relation = self.create_feedback_relation(
            organizer=organizer_group.group
        )
        email = get_committee_email(feedback_relation)
        self.assertEqual(email, organizer_group.email)

        # Default
        feedback_relation = self.create_feedback_relation()
        email = get_committee_email(feedback_relation)
        self.assertEqual(email, settings.DEFAULT_FROM_EMAIL)

        # Not existing
        feedback_relation = self.create_void_feedback_relation()
        email = get_committee_email(feedback_relation)
        self.assertEqual(email, "missing mail")

    def test_group_email(self):
        # Feedback email should be be to the organizing committee
        organizer_group: Group = G(Group)
        online_group: OnlineGroup = G(
            OnlineGroup, group=organizer_group, email="testkom@example.com"
        )
        feedback_relation = self.create_feedback_relation(
            event_type=1, organizer=organizer_group
        )
        email = get_committee_email(feedback_relation)
        self.assertEqual(email, online_group.email)
        self.assertNotEqual(email, settings.EMAIL_ARRKOM)

    def test_date(self):
        feedback_relation = self.create_feedback_relation()
        date = end_date(feedback_relation)
        self.assertEqual(date, self.yesterday().date())

    def test_void_date(self):
        feedback_relation = self.create_void_feedback_relation()
        date = end_date(feedback_relation)
        self.assertFalse(date)

    def test_mark_setting(self):
        users = [User.objects.get(username="user1")]
        all_users = User.objects.all()
        set_marks("test_title", users)
        mark = Mark.objects.get()

        self.assertEqual(set(users), set([mu.user for mu in mark.given_to.all()]))
        self.assertNotEqual(
            set(all_users), set([mu.user for mu in mark.given_to.all()])
        )

    def test_login(self):
        client = Client()
        self.assertTrue(client.login(username="user1", password="Herpaderp123"))

    def test_post_incorrect(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")
        feedback_relation = self.create_feedback_relation()
        response = client.post(feedback_relation.get_absolute_url())
        for i in range(len(response.context["questions"])):
            self.assertIn(
                str(_("This field is required.")),
                response.context["questions"][i].errors["answer"],
            )

    def test_should_redirect(self):  # Login_required / not logged inn
        response = self.client.get("/feedback/events/event/100/1/")
        self.assertEqual(response.status_code, 302)

    def test_bad_urls(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")

        response = client.get("/feedback/events/event/100/1/")
        self.assertEqual(response.status_code, 404)

        response = client.get("/feedback/events/event/1/100/")
        self.assertEqual(response.status_code, 404)

        response = client.get("/feedback/events/event/100/100/")
        self.assertEqual(response.status_code, 404)

        response = client.get("/feedback/events/derp/1/1/")
        self.assertEqual(response.status_code, 404)

    # TODO test tokens
    # TODO test permissions when implemented


class FeedbackViewTestCase(FeedbackTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.organizer: Group = G(Group)
        self.organizer.user_set.add(self.user1)

        self.feedback_relation = self.create_feedback_relation(organizer=self.organizer)
        self.feedback_url = reverse(
            "feedback",
            args=(
                "events",
                "event",
                str(self.event.id),
                str(self.feedback_relation.id),
            ),
        )
        self.results_url = reverse(
            "result",
            args=(
                "events",
                "event",
                str(self.event.id),
                str(self.feedback_relation.id),
            ),
        )
        self.client.force_login(self.user1, backend=None)

    def test_user_can_load_feedback_page(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, 200)

    def test_non_attendee_user_cannot_load_feedback_page(self):
        user3: User = G(User)
        self.client.force_login(user3)
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, 302)

    def test_organizer_can_access_results(self):
        response = self.client.get(self.results_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_results(self):
        admin_user: User = G(User, is_superuser=True)
        self.client.force_login(admin_user)
        response = self.client.get(self.results_url)
        self.assertEqual(response.status_code, 200)

    def test_regular_cannot_access_results(self):
        admin_user: User = G(User, is_superuser=False)
        self.client.force_login(admin_user)
        response = self.client.get(self.results_url)
        self.assertEqual(
            response.status_code, 302
        )  # No access returns a redirect for feedback results
