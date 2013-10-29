import logging
import datetime
from pytz import timezone

from django_dynamic_fixture import G
from django.conf import settings
from django.test import TestCase

from apps.authentication.models import OnlineUser as User, AllowedUsername
from apps.events.models import (Event, AttendanceEvent, Attendee,
                                RuleBundle, RuleOffset,
                                FieldOfStudyRule, GradeRule, UserGroupRule)
from apps.marks.models import Mark, UserEntry

class EventTest(TestCase):

    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(AttendanceEvent, event=self.event)
        self.user = G(User)
        self.user.username = 'ola123'
        self.user.ntnu_username = 'ola123ntnu'
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

    def testMarksDelay(self):
        self.logger.debug("Testing signup with marks.")
        now = datetime.datetime.now(timezone(settings.TIME_ZONE))
        # Setting registration start 1 hour in the past, end one week in the future.
        self.attendance_event.registration_start = now - datetime.timedelta(hours=1)
        self.attendance_event.registration_end = now + datetime.timedelta(days=7)
        # Making the user a member.
        allowed_username = G(AllowedUsername, username='ola123ntnu', expiration_date = now + datetime.timedelta(weeks=1))
       
        # The user should be able to attend now, since the event has no rule bundles.
        response = self.event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        
        # Giving the user a mark to see if the status goes to False.
        mark1 = G(Mark, title='Testprikk12345')
        userentry = G(UserEntry, user=self.user, mark=mark1)
        response = self.event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
