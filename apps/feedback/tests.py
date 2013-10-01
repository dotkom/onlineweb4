"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from apps.feedback.feedback_mail import FeedbackMail, Message
from apps.feedback.models import Feedback, FeedbackRelation, Attendee
from apps.events.models import Event, AttendanceEvent
from apps.authentication.models import OnlineUser as User
from datetime import datetime

class SimpleTest(TestCase):
    fixtures = ["test_feedback_fixture.json"]

    def setUp(self):
        user1 = User.objects.create(username="user1", email="user1@mail.com")
        user2 = User.objects.create(username="user2", email="user2@mail.com")
        event1 = Event.objects.create(title="Bedpress", event_start = datetime.today(), event_end= datetime.today(), event_type = 2, author = user1)
        event2 = Event.objects.create(title="Kurs", event_start = datetime.today(), event_end= datetime.today(), event_type = 3, author = user1)
        event3 = Event.objects.create(title="Sosial Happening", event_start = datetime.today(), event_end= datetime.today(), event_type = 1, author = user1)
        attendanceEvent1 = AttendanceEvent.objects.create(registration_start = datetime.today(), registration_end = datetime.today(), event = event1)
        attendanceEvent2 = AttendanceEvent.objects.create(registration_start = datetime.today(), registration_end = datetime.today(), event = event2)
        attendanceEvent3 = AttendanceEvent.objects.create(registration_start = datetime.today(), registration_end = datetime.today(), event = event3)
        feedback = Feedback.objects.create(author = user1)
        atendee1 = Attendee.objects.create(event = event1, user = user1)
        atendee2 = Attendee.objects.create(event = event1, user = user2)

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
