import datetime
import logging

from django_dynamic_fixture import G
from django.conf import settings
from django.test import TestCase
from django.utils import timezone

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
        # Setting registration start 1 hour in the past, end one week in the future.
        self.now = timezone.now()
        self.attendance_event.registration_start = self.now - datetime.timedelta(hours=1)
        self.attendance_event.registration_end = self.now + datetime.timedelta(days=7)
        # Making the user a member.
        self.allowed_username = G(AllowedUsername, username='ola123ntnu', expiration_date = self.now + datetime.timedelta(weeks=1))

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

    def testSignUpWithNoRulesNoMarks(self):
        self.logger.debug("Testing signup with no rules and no marks.")
       
        # The user should be able to attend now, since the event has no rule bundles.
        response = self.event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEquals(200, response['status_code'])
        
    def testSignUpWithNoRulesAndAMark(self):
        self.logger.debug("Testing signup with no rules and a mark.")

        # Giving the user a mark to see if the status goes to False.
        mark1 = G(Mark, title='Testprikk12345')
        userentry = G(UserEntry, user=self.user, mark=mark1)
        response = self.event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEquals(400, response['status_code'])

    def testRuleOffsets(self):
        self.logger.debug("Testing rule offsets.")
        offset = G(RuleOffset, offset=24)
        self.assertEquals(offset.offset, 24)

    def testGradeRule(self):
        self.logger.debug("Testing restriction with grade rules.")

        # Create the offset, rule and rule_bundles
        self.offset = G(RuleOffset, offset=24)
        self.assertEquals(self.offset.offset, 24)
        self.graderule = G(GradeRule, grade=1)
        self.assertEquals(self.graderule.grade, 1)
        self.graderule.offset = self.offset 
        self.assertEquals(self.graderule.offset.offset, 24)
        self.assertEquals(unicode(self.graderule), u"1. klasse etter 24 timer")
        self.rule_bundle = G(RuleBundle) 
        self.rule_bundle.grade_rules.add(self.graderule)
        self.assertEqual("", unicode(self.rule_bundle))

        self.attendance_event.rule_bundles.add(self.rule_bundle)
        
        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(411, response['status_code'])

        # Make the user a grade 1 and try again.
        self.user.field_of_study = 1
        self.user.started_date = self.now.date()
        response = self.event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(212, response['status_code'])
