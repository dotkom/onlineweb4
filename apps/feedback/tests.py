# -*- encoding: utf-8 -*-
import logging

from django.utils import timezone as timezone
from datetime import timedelta

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.test.client import Client

from apps.feedback.mommy import FeedbackMail
from apps.feedback.models import Feedback, FeedbackRelation, TextQuestion, RatingQuestion
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.marks.models import Mark
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Email


class SimpleTest(TestCase):

    # Feedback mail
    def setUp(self):

        self.logger = logging.getLogger()

        # Setup users
        self.user1 = User.objects.create(username="user1", is_active=True, is_staff=True)
        Email.objects.create(user=self.user1, email="user1@gmail.com", primary=True)
        self.user2 = User.objects.create(username="user2")
        Email.objects.create(user=self.user2, email="user2@gmail.com", primary=True)

        self.user1.set_password("Herpaderp123")
        self.user1.save()

    def yesterday(self):
        return timezone.now() - timedelta(days=1)

    def tomorow(self):
        return timezone.now() + timedelta(days=1)

    def create_feedback_relation(self, end_date=False, event_type=2, feedback=None, deadline=False):
        if not end_date:
            end_date = self.yesterday()

        if not deadline:
            deadline = timezone.now().date() + timedelta(days=4)

        event = Event.objects.create(
            title="-",
            event_start=self.yesterday(),
            event_end=end_date,
            event_type=event_type,
            author=self.user1
        )

        attendance_event = AttendanceEvent.objects.create(
            registration_start=timezone.now(),
            unattend_deadline=timezone.now(),
            registration_end=timezone.now(),
            event=event,
            max_capacity=30
        )

        feedback = Feedback.objects.create(author=self.user1)
        TextQuestion.objects.create(feedback=feedback)
        RatingQuestion.objects.create(feedback=feedback)

        Attendee.objects.create(event=attendance_event, user=self.user1, attended=True)
        Attendee.objects.create(event=attendance_event, user=self.user2, attended=True)
        return FeedbackRelation.objects.create(feedback=feedback, content_object=event, deadline=deadline, active=True)

    # Create a feedback relation that won't work
    def create_void_feedback_relation(self):
        feedback = Feedback.objects.create(author=self.user1)
        deadline = self.tomorow()
        return FeedbackRelation.objects.create(
            feedback=feedback,
            content_object=self.user1,
            deadline=deadline,
            active=True
        )

    def test_users_mail_addresses(self):
        feedback_relation = self.create_feedback_relation()

        # The below if user.id check is due to Django Guardian middleware needing an AnonymousUser, that has ID -1
        user_mails = [user.email for user in User.objects.all() if user.id >= 0]

        message = FeedbackMail.generate_message(feedback_relation, self.logger)
        self.assertEqual(set(message.attended_mails), set(user_mails))

    def test_event_not_done(self):
        feedback_relation = self.create_feedback_relation(end_date=timezone.now())
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Event not done")
        self.assertFalse(message.send)

    def test_user_answered(self):
        feedback_relation = self.create_feedback_relation()
        feedback_relation.answered = [self.user1]
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        not_answered = [self.user2.email]
        self.assertEqual(set(message.attended_mails), set(not_answered))

    def test_everyone_answered(self):
        feedback_relation = self.create_feedback_relation()
        feedback_relation.answered = [self.user1, self.user2]
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, 'Everyone has answered')
        self.assertFalse(message.send)
        self.assertFalse(feedback_relation.active)

    def test_deadline_passeed(self):
        feedback_relation = self.create_feedback_relation(deadline=self.yesterday().date())
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Deadine passed")
        self.assertFalse(feedback_relation.active)

    def test_last_warning(self):
        feedback_relation = self.create_feedback_relation(deadline=timezone.now().date())
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Last warning")
        self.assertTrue(message.send)

    def test_warning(self):
        feedback_relation = self.create_feedback_relation(deadline=timezone.now().date() + timedelta(days=2))
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "Warning message")
        self.assertTrue(message.send)

    def test_first_mail(self):
        feedback_relation = self.create_feedback_relation()
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "First message")
        self.assertTrue(message.send)
        self.assertTrue(feedback_relation.first_mail_sent)

    def test_no_message(self):
        feedback_relation = self.create_feedback_relation(end_date=timezone.now() - timedelta(days=2))
        feedback_relation.first_mail_sent = True
        message = FeedbackMail.generate_message(feedback_relation, self.logger)

        self.assertEqual(message.status, "No message generated")
        self.assertFalse(message.send)

    def test_committee_mails(self):
        # Sosialt
        feedback_relation = self.create_feedback_relation(event_type=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)

        # Bedkom
        feedback_relation = self.create_feedback_relation()  # Default param is event_type=2
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_BEDKOM)

        # Kurs
        feedback_relation = self.create_feedback_relation(event_type=3)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_FAGKOM)

        # Utflukt
        feedback_relation = self.create_feedback_relation(event_type=4)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)

        # Ekskursjon
        feedback_relation = self.create_feedback_relation(event_type=5)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_EKSKOM)

        # Default
        feedback_relation = self.create_feedback_relation(event_type=6)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.DEFAULT_FROM_EMAIL)

        # Not existing
        feedback_relation = self.create_void_feedback_relation()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, "missing mail")

    def test_date(self):
        feedback_relation = self.create_feedback_relation()
        date = FeedbackMail.end_date(feedback_relation)
        self.assertEqual(date, self.yesterday().date())

    def test_void_date(self):
        feedback_relation = self.create_void_feedback_relation()
        end_date = FeedbackMail.end_date(feedback_relation)
        self.assertFalse(end_date)

    def test_mark_setting(self):
        users = [User.objects.get(username='user1')]
        all_users = User.objects.all()
        FeedbackMail.set_marks("test_title", users)
        mark = Mark.objects.get()

        self.assertEqual(set(users), set([mu.user for mu in mark.given_to.all()]))
        self.assertNotEqual(set(all_users), set([mu.user for mu in mark.given_to.all()]))

    def test_login(self):
        client = Client()
        self.assertTrue(client.login(username="user1", password="Herpaderp123"))

    def test_post_incorrect(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")
        feedback_relation = self.create_feedback_relation()
        response = client.post(feedback_relation.get_absolute_url())
        for i in range(len(response.context['answers'])):
            self.assertIn(
                str(_('This field is required.')),
                response.context['answers'][i].errors['answer']
            )

    """
    Disabled because request.META['HTTP_HOST'] apperantly is not supported by the test client
    def test_good_urls(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        response = client.post(feedback_relation.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = client.get(feedback_relation.get_absolute_url() + 'results/')
        self.assertEqual(response.status_code, 200)
    """

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
