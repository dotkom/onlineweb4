import logging

from django_dynamic_fixture import G
from django.test import TestCase

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event, AttendanceEvent, Attendee

class EventTest(TestCase):

    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(AttendanceEvent, event=self.event)
        self.user = G(User)
        self.attendee = G(Attendee, event=self.attendance_event, user=self.user)
        self.logger = logging.getLogger(__name__)

    def testEventUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on Event with dynamic fixtures")
        self.assertEqual(self.event.__unicode__(), u'Sjakkturnering')

    def testAttendanceEventUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on AttendanceEvent with dynamic fixtures")
        self.assertEqual(self.attendance_event.__unicode__(), u'Sjakkturnering')

    def testAttendeeUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on Attendee with dynamic fixtures")
        self.assertEqual(self.attendee.__unicode__(), self.user.get_full_name())
        self.assertNotEqual(self.attendee.__unicode__(), 'Ola Normann')
