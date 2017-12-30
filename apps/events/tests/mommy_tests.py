import datetime

from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import AllowedUsername
from apps.events.models import AttendanceEvent, Attendee, Event
from apps.events.mommy import SetEventMarks
from apps.marks.models import MarkUser


class EventTest(TestCase):
    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(
            AttendanceEvent, event=self.event, max_capacity=2)
        self.user = G(User, username='ola123', ntnu_username='ola123ntnu',
                      first_name="ola", last_name="nordmann")
        # Setting registration start 1 hour in the past, end one week in the future.
        self.now = timezone.now()
        self.attendance_event.registration_start = self.now - \
            datetime.timedelta(hours=1)
        self.attendance_event.registration_end = self.now + \
            datetime.timedelta(days=7)
        # Making the user a member.
        self.allowed_username = G(AllowedUsername, username='ola123ntnu',
                                  expiration_date=self.now + datetime.timedelta(weeks=1))

    def testMommyNotAttended(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=False)
        self.assertEqual([self.user], self.attendance_event.not_attended())

    def testMommyAttended(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=True)
        self.assertEqual([], self.attendance_event.not_attended())

    def testMommyActiveEvents(self):
        self.attendance_event.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.event.save()

        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.attendance_event.save()

        self.assertEqual(self.attendance_event,
                         SetEventMarks.active_events()[0])

    def testMommyMarksHasBeenSet(self):
        self.attendance_event.marks_has_been_set = True
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        self.assertFalse(SetEventMarks.active_events())

    def testMommyDontAutmaticallySetMarks(self):
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = False
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        self.assertFalse(SetEventMarks.active_events())

    def testMommyEventNotDone(self):
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() + datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        self.assertFalse(SetEventMarks.active_events())

    def testMommySetMarks(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=False)
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        SetEventMarks.setMarks(self.attendance_event)

        self.assertTrue(self.attendance_event.marks_has_been_set)
        self.assertEqual(self.user, MarkUser.objects.get().user)

    def testMommyEveryoneAttendend(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=True)
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        SetEventMarks.setMarks(self.attendance_event)

        self.assertTrue(self.attendance_event.marks_has_been_set)
        self.assertFalse(MarkUser.objects.all())

    def testMommyGenerateEmptyMessage(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=True)
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        message = SetEventMarks.generate_message(self.attendance_event)

        self.assertFalse(message.send)
        self.assertFalse(message.results_message)

    def testMommyGenerateMessage(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=False)
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        message = SetEventMarks.generate_message(self.attendance_event)

        self.assertTrue(message.send)
        self.assertTrue(message.committee_message)
