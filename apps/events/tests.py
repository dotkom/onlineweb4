from apps.events.models import Event, AttendanceEvent, Attendee
from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_not_equal
from django_dynamic_fixture import G
import logging

event = G(Event, title='Sjakkturnering')
attendance_event = G(AttendanceEvent, event=event)
user = G(User)
attendee = G(Attendee, event=attendance_event, user=user)
logger = logging.getLogger(__name__)


def testEventUnicodeIsCorrect():
    logger.debug("Testing testing on Event with dynamic fixtures")
    assert_equal(event.__unicode__(), u'Sjakkturnering')


def testAttendanceEventUnicodeIsCorrect():
    logger.debug("Testing testing on AttendanceEvent with dynamic fixtures")
    assert_equal(attendance_event.__unicode__(), u'Sjakkturnering')


def testAttendeeUnicodeIsCorrect():
    logger.debug("Testing testing on Attendee with dynamic fixtures")
    assert_equal(attendee.__unicode__(), user.get_full_name())
    assert_not_equal(attendee.__unicode__(), 'Ola Normann')
