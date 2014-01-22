"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import timezone as timezone
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.test.client import Client

from apps.feedback.mommy import FeedbackMail, Message
from apps.feedback.models import Feedback, FeedbackRelation, TextQuestion, RatingQuestion
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.marks.models import Mark
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Email
from apps.authentication.forms import LoginForm

class SimpleTest(TestCase):

    #Feedback mail 
    def setUp(self):
        user1 = User.objects.create(username="user1", is_active=True, is_staff=True)
        user1.set_password("Herpaderp123")
        user1.save()
        Email.objects.create(user = user1, email="user1@gmail.com", primary=True)
        user2 = User.objects.create(username="user2")
        Email.objects.create(user = user2, email="user2@gmail.com", primary=True)
        event = Event.objects.create(title="Bedpress", event_start = timezone.now(), event_end = timezone.now(), event_type = 2, author = user1)
        attendance_event = AttendanceEvent.objects.create(
                                                        registration_start = timezone.now(), 
                                                        unattend_deadline = timezone.now(), 
                                                        registration_end = timezone.now(), 
                                                        event = event, 
                                                        max_capacity=30
                                                        )
        feedback = Feedback.objects.create(author = user1)
        TextQuestion.objects.create(feedback = feedback)
        RatingQuestion.objects.create(feedback = feedback)
        atendee1 = Attendee.objects.create(event = attendance_event, user = user1, attended=True)
        atendee2 = Attendee.objects.create(event = attendance_event, user = user2, attended =True)
        FeedbackRelation.objects.create(feedback=feedback, content_object=event, deadline=timezone.now(), active=True)
        FeedbackRelation.objects.create(feedback=feedback, content_object=atendee1, deadline=timezone.now(), active=True)


    def test_attendees(self):
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        message = FeedbackMail.generate_message(feedback_relation)
        user_mails = [str(user.get_email()) for user in User.objects.all()]

        self.assertEqual(set(message.attended_mails), set(user_mails))

        user1 = User.objects.get(pk=1)
        feedback_relation.answered = [user1]

        message = FeedbackMail.generate_message(feedback_relation)
        user_mails = [str(user.get_email()) for user in [User.objects.get(pk=2)]]
        self.assertEqual(set(message.attended_mails), set(user_mails))

        feedback_relation = FeedbackRelation.objects.get(pk=2)
        message = FeedbackMail.generate_message(feedback_relation)

        self.assertFalse(message.send)

    def test_committee_mails(self):
        event = Event.objects.get()

        #Sosialt
        event.event_type = 1
        event.save()
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)
        
        #Bedkom
        event.event_type = 2
        event.save()
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_BEDKOM)

        #Kurs
        event.event_type = 3
        event.save()
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_FAGKOM)
        
        #Utflukt
        event.event_type = 4
        event.save()
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)
        
        #Default
        event.event_type = 5
        event.save()
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.DEFAULT_FROM_EMAIL)
        
        feedback_relation2 = FeedbackRelation.objects.get(pk=2)
        email = FeedbackMail.get_committee_email(feedback_relation2)
        self.assertEqual(email, "missing mail")
 
    def test_start_date(self):
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        start_date = FeedbackMail.start_date(feedback_relation)

        self.assertEqual(start_date, timezone.now().date())

        feedback_relation2 = FeedbackRelation.objects.get(pk=2)
        start_date = FeedbackMail.start_date(feedback_relation2)
        self.assertFalse(start_date)

    def test_active(self):
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        yesterday = timezone.now() - timedelta(days=1)
        feedback_relation.deadline = yesterday.date()
        feedback_relation.active = True
        feedback_relation.save()
        FeedbackMail.generate_message(feedback_relation)

        self.assertFalse(feedback_relation.active)

    def test_marks(self):
        users = [User.objects.get(pk=1)]
        all_users = User.objects.all()
        FeedbackMail.set_marks("test_title", users)
        mark = Mark.objects.get()

        self.assertEqual(set(users), set(mark.given_to.all()))
        self.assertNotEqual(set(all_users), set(mark.given_to.all()))

    def test_post_correct(self):
        #TODO: do eeet! test posted against db (Sigurd) 2013-02-08
        pass

    def test_login(self):
        client = Client()
        self.assertTrue(client.login(username="user1", password="Herpaderp123"))

    def test_post_incorrect(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        response = client.post(feedback_relation.get_absolute_url())
        for i in range(len(response.context['answers'])):
            self.assertIn(unicode(_(u'This field is required.')),
                          response.context['answers'][i].errors['answer'])

    '''
    Disabled because request.META['HTTP_HOST'] apperantly is not supported by the test client
    def test_good_urls(self):
        client = Client()
        client.login(username="user1", password="Herpaderp123")
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        response = client.post(feedback_relation.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = client.get(feedback_relation.get_absolute_url() + 'results/')
        self.assertEqual(response.status_code, 200)
    '''
    
    def test_bad_urls(self):
        response = self.client.get("/feedback/events/event/100/1/")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/feedback/events/event/1/100/")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/feedback/events/event/100/100/")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/feedback/events/derp/1/1/")
        self.assertEqual(response.status_code, 404)
