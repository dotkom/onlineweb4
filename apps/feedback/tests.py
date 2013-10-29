"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from pytz import timezone as _timezone

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from apps.feedback.feedback_mails import FeedbackMail, Message
from apps.feedback.models import Feedback, FeedbackRelation
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.marks.models import Mark
from apps.authentication.models import OnlineUser as User
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

class SimpleTest(TestCase):

    #Feedback mail 
    def setUp(self):
        user1 = User.objects.create(username="user1", email="user1@mail.com")
        user2 = User.objects.create(username="user2", email="user2@mail.com")
        event = Event.objects.create(title="Bedpress", event_start = datetime.now(_timezone(settings.TIME_ZONE)), event_end= datetime.now(_timezone(settings.TIME_ZONE)), event_type = 2, author = user1)
        attendance_event = AttendanceEvent.objects.create(registration_start = datetime.now(_timezone(settings.TIME_ZONE)), registration_end = datetime.now(_timezone(settings.TIME_ZONE)), event = event, max_capacity=30)
        feedback = Feedback.objects.create(author = user1)
        atendee1 = Attendee.objects.create(event = attendance_event, user = user1)
        atendee2 = Attendee.objects.create(event = attendance_event, user = user2)
        FeedbackRelation.objects.create(feedback=feedback, content_object=event, deadline=datetime.now(_timezone(settings.TIME_ZONE)), active=True)
        FeedbackRelation.objects.create(feedback=feedback, content_object=atendee1, deadline=datetime.now(_timezone(settings.TIME_ZONE)), active=True)


    def test_attendees(self):
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        message = FeedbackMail.generate_message(feedback_relation)
        user_mails = [user.email for user in User.objects.all()]

        self.assertEqual(set(message.attended_mails), set(user_mails))

        user1 = User.objects.get(pk=1)
        feedback_relation.answered = [user1]

        message = FeedbackMail.generate_message(feedback_relation)
        user_mails = [user.email for user in [User.objects.get(pk=2)]]
        self.assertEqual(set(message.attended_mails), set(user_mails))

        feedback_relation = FeedbackRelation.objects.get(pk=2)
        message = FeedbackMail.generate_message(feedback_relation)

        self.assertEqual(message, None)

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

        self.assertEqual(start_date, datetime.now().date())

        feedback_relation2 = FeedbackRelation.objects.get(pk=2)
        start_date = FeedbackMail.start_date(feedback_relation2)
        self.assertFalse(start_date)

    def test_active(self):
        feedback_relation = FeedbackRelation.objects.get(pk=1)
        yesterday = datetime.now() - timedelta(days=1)
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

#    def test_post_incorrect(self):
#        resp = self.client.post("/feedback/auth/user/1/1/")
#        self.assertEqual(resp.status_code, 200)
#        for i in range(len(resp.context['answers'])):
#            self.assertIn(unicode(_(u'This field is required.')),
#                          resp.context['answers'][i].errors['answer'])
#    
#    def test_good_urls(self):
#        resp = self.client.get("/feedback/auth/user/1/1/")
#        self.assertEqual(resp.status_code, 200)
#
#        resp = self.client.get("/feedback/auth/user/1/1/results")
#        self.assertEqual(resp.status_code, 200)
#
#    def test_bad_urls(self):
#        resp = self.client.get("/feedback/auth/user/100/1/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/user/1/100/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/user/100/100/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/derp/1/1/")
#        self.assertEqual(resp.status_code, 404)
