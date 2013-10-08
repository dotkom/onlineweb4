"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from apps.feedback.feedback_mails import FeedbackMail, Message
from apps.feedback.models import Feedback, FeedbackRelation
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.authentication.models import OnlineUser as User
from datetime import datetime, timedelta
from django.conf import settings

class SimpleTest(TestCase):

    #Feedback mail 
    def setUp(self):
        user1 = User.objects.create(username="user1", email="user1@mail.com")
        user2 = User.objects.create(username="user2", email="user2@mail.com")
        event = Event.objects.create(title="Bedpress", event_start = datetime.today(), event_end= datetime.today(), event_type = 2, author = user1)
        attendance_event = AttendanceEvent.objects.create(registration_start = datetime.today(), registration_end = datetime.today(), event = event, max_capacity=30)
        feedback = Feedback.objects.create(author = user1)
        atendee1 = Attendee.objects.create(event = attendance_event, user = user1)
        atendee2 = Attendee.objects.create(event = attendance_event, user = user2)
        FeedbackRelation.objects.create(feedback=feedback, content_object=event, deadline=datetime.today(), active=True)


    def test_test_attendees(self):
        feedback_relation = FeedbackRelation.objects.get()
        message = FeedbackMail.generate_message(feedback_relation)

        self.assertEqual(message.attended_mails[0], "user1@mail.com")
        self.assertEqual(message.attended_mails[1], "user2@mail.com")

    def test_committee_mails(self):
        event = Event.objects.get()

        #Sosialt
        event.event_type = 1
        event.save()
        feedback_relation = FeedbackRelation.objects.get()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)
        
        #Bedkom
        event.event_type = 2
        event.save()
        feedback_relation = FeedbackRelation.objects.get()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_BEDKOM)

        #Kurs
        event.event_type = 3
        event.save()
        feedback_relation = FeedbackRelation.objects.get()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_PROKOM)
        
        #Utflukt
        event.event_type = 4
        event.save()
        feedback_relation = FeedbackRelation.objects.get()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.EMAIL_ARRKOM)
        
        #Default
        event.event_type = 5
        event.save()
        feedback_relation = FeedbackRelation.objects.get()
        email = FeedbackMail.get_committee_email(feedback_relation)
        self.assertEqual(email, settings.DEFAULT_FROM_EMAIL)
 
    def test_start_date(self):
        feedback_relation = FeedbackRelation.objects.get()
        start_date = FeedbackMail.start_date(feedback_relation)

        self.assertEqual(start_date, datetime.today().date())

    def test_get_link(self):
        feedback_relation = FeedbackRelation.objects.get()
        link = FeedbackMail.get_link(feedback_relation)
        #TODO
        pass


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
