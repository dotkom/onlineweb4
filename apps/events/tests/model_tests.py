from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent, Reservation, Event
from apps.feedback.models import Feedback, FeedbackRelation


class AttendanceEventModelTest(TestCase):
    def create_attendance_event(self):
        event = G(Event)
        return G(AttendanceEvent, event=event)
    
    def add_feedback(self, attendance_event):
        feedback = G(Feedback)
        return G(
            FeedbackRelation, feedback=feedback, object_id=attendance_event.event_id,
            content_type=ContentType.objects.get_for_model(Event)
        )

    def add_reservation(self, attendance_event):
        return G(Reservation, attendance_event=attendance_event)

    def test_get_feedback(self):
        attendance_event = self.create_attendance_event()
        feedback_relation = self.add_feedback(attendance_event)

        attendance_event_feedback = attendance_event.get_feedback()

        self.assertEqual(attendance_event_feedback, feedback_relation)

    def test_has_feedback_true(self):
        attendance_event = self.create_attendance_event()
        self.add_feedback(attendance_event)

        has_feedback = attendance_event.has_feedback()

        self.assertTrue(has_feedback)

    def test_has_feedback_false(self):
        attendance_event = self.create_attendance_event()

        has_feedback = attendance_event.has_feedback()

        self.assertFalse(has_feedback)

    def test_has_reservation(self):
        attendance_event = self.create_attendance_event()

        self.assertFalse(attendance_event.has_reservation)

        self.add_reservation(attendance_event)

        self.assertTrue(attendance_event.has_reservation)
