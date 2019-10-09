import datetime

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.authentication.models import AllowedUsername
from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company
from apps.events.models import (AttendanceEvent, Attendee, CompanyEvent, Event, FieldOfStudyRule,
                                GradeRule, GroupRestriction, Reservation, Reservee, RuleBundle,
                                UserGroupRule)
from apps.feedback.models import Feedback, FeedbackRelation
from apps.marks.models import DURATION, Mark, MarkUser

from .utils import attend_user_to_event, generate_attendance_event, generate_attendee


class EventModelTest(TestCase):
    def test_event_unicode(self):
        event = G(Event, title='Sjakkturnering')

        self.assertEqual(event.__str__(), 'Sjakkturnering')

    def test_company_event_method_returns_company_events(self):
        event = G(Event, title='Sjakkturnering')
        company1 = G(CompanyEvent, event=event, company=G(Company))
        company2 = G(CompanyEvent, event=event, company=G(Company))

        companies = event.company_event

        self.assertIn(company1, companies)
        self.assertIn(company2, companies)


class AttendanceEventModelTest(TestCase):
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

    def test_attendanceEventUnicode_IsCorrect(self):
        self.assertEqual(self.attendance_event.__str__(), 'Sjakkturnering')

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

    def test_attendee_waitlist_qs(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        user1 = G(User, username="jan", first_name="jan")
        G(Attendee, event=self.attendance_event, user=user1)
        user2 = G(User, username="per", first_name="per")
        G(Attendee, event=self.attendance_event, user=user2)
        user3 = G(User, username="gro", first_name="gro")
        G(Attendee, event=self.attendance_event, user=user3)
        self.assertEqual(self.attendance_event.max_capacity, 2)
        self.assertEqual(self.attendance_event.number_of_attendees, 2)
        self.assertEqual(self.attendance_event.number_on_waitlist, 2)

    def test_reserved_seats(self):
        reservation = G(
            Reservation, attendance_event=self.attendance_event, seats=2)
        G(Reservee, reservation=reservation, name="jan",
          note="jan er kul", allergies="allergi1")
        self.assertEqual(
            self.attendance_event.number_of_reserved_seats_taken, 1)
        G(Reservee, reservation=reservation, name="per",
          note="per er rå", allergies="allergi2")
        self.assertEqual(
            self.attendance_event.number_of_reserved_seats_taken, 2)

    def test_number_of_taken_seats(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=False)
        # Increase event capacity so we have more room to test with
        self.attendance_event.max_capacity = 5
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        # Make a reservation, for 2 seats
        reservation = G(
            Reservation, attendance_event=self.attendance_event, seats=2)
        G(Reservee, reservation=reservation, name="jan",
          note="jan er kul", allergies="allergi1")
        self.assertEqual(self.attendance_event.max_capacity, 5)
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(
            self.attendance_event.number_of_reserved_seats_taken, 1)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        G(Reservee, reservation=reservation, name="per",
          note="per er rå", allergies="allergi2")
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(
            self.attendance_event.number_of_reserved_seats_taken, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        user3 = G(User, username="gro", first_name="gro")
        G(Attendee, event=self.attendance_event, user=user3)
        self.assertEqual(self.attendance_event.number_of_attendees, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 4)

    def testSignUpWithNoRulesNoMarks(self):
        # The user should be able to attend now, since the event has no rule bundles.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEqual(200, response['status_code'])

    def testSignUpWithNoRulesNoMarksNoMembership(self):
        self.allowed_username.delete()
        # The user should not be able to attend, since the event has no rule bundles
        # and they are not a member.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(400, response['status_code'])

    def testSignUpWithNoRulesAndAMark(self):
        # Giving the user a mark to see if the status goes to False.
        mark1 = G(Mark, title='Testprikk12345')
        G(MarkUser, user=self.user, mark=mark1,
          expiration_date=self.now + datetime.timedelta(days=DURATION))
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(401, response['status_code'])

    def testFieldOfStudyRule(self):
        # Create the rule and rule_bundles
        self.fosrule = G(FieldOfStudyRule, field_of_study=1, offset=24)
        self.assertEqual(self.fosrule.field_of_study, 1)
        self.assertEqual(self.fosrule.offset, 24)
        self.assertEqual(str(self.fosrule),
                         "Bachelor i Informatikk etter 24 timer")
        self.rulebundle = G(RuleBundle, description='')
        self.rulebundle.field_of_study_rules.add(self.fosrule)
        self.assertEqual(str(self.rulebundle),
                         "Bachelor i Informatikk etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rulebundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(410, response['status_code'])

        # Make the user a bachelor and try again. Should get message about offset.
        self.user.field_of_study = 1
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(420, response['status_code'])

        # Add a new grade rule with no offset and see if signup works
        self.fosrule2 = G(FieldOfStudyRule, field_of_study=1, offset=0)
        self.rulebundle.field_of_study_rules.add(self.fosrule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEqual(210, response['status_code'])

    def testGradeRule(self):
        # Create the rule and rule_bundles
        self.graderule = G(GradeRule, grade=1, offset=24)
        self.assertEqual(self.graderule.grade, 1)
        self.assertEqual(self.graderule.offset, 24)
        self.assertEqual(str(self.graderule), "1. klasse etter 24 timer")
        self.rulebundle = G(RuleBundle, description='')
        self.rulebundle.grade_rules.add(self.graderule)
        self.assertEqual(str(self.rulebundle), "1. klasse etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rulebundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(411, response['status_code'])

        # Make the user a grade 1 and try again. Should get message about offset.
        self.user.field_of_study = 1
        self.user.started_date = self.now.date()
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(421, response['status_code'])

        # Add a new grade rule with no offset and see if signup works
        self.graderule2 = G(GradeRule, grade=1, offset=0)
        self.rulebundle.grade_rules.add(self.graderule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEqual(211, response['status_code'])

    def testUserGroupRule(self):
        # Create the rule and rule_bundles
        self.group = G(Group, name="Testgroup")
        self.grouprule = G(UserGroupRule, group=self.group, offset=24)
        self.assertEqual(self.grouprule.group, self.group)
        self.assertEqual(self.grouprule.offset, 24)
        self.assertEqual(str(self.grouprule), "Testgroup etter 24 timer")
        self.rulebundle = G(RuleBundle, description='')
        self.rulebundle.user_group_rules.add(self.grouprule)
        self.assertEqual(str(self.rulebundle), "Testgroup etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rulebundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(412, response['status_code'])

        # Make the user a grade 1 and try again. Should get message about offset
        self.user.groups.add(self.group)
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(422, response['status_code'])

        # Add a new grade rule with no offset and see if signup works
        self.grouprule2 = G(UserGroupRule, group=self.group, offset=0)
        self.rulebundle.user_group_rules.add(self.grouprule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEqual(212, response['status_code'])

    def testFutureAccessTrumpsOffset(self):
        # Create two different rules, and verify that the response is false, but without offset
        # Group rule
        self.group = G(Group, name="Testgroup")
        self.grouprule = G(UserGroupRule, group=self.group, offset=0)
        self.user.groups.add(self.group)
        # Grade rule
        self.graderule = G(GradeRule, grade=1, offset=24)
        self.user.field_of_study = 1
        self.user.started_date = self.now.date()
        # Make the rule bundle
        self.rulebundle = G(RuleBundle, description='')
        self.rulebundle.grade_rules.add(self.graderule)
        self.rulebundle.user_group_rules.add(self.grouprule)
        self.attendance_event.rule_bundles.add(self.rulebundle)
        # Move registration start into the future
        self.attendance_event.registration_start = self.now + \
            datetime.timedelta(hours=1)
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(402, response['status_code'])

    def testRestrictedEvents(self):
        allowed_groups = [G(Group), G(Group)]
        allowed_user = G(User, groups=[allowed_groups[0], ])

        denied_groups = [G(Group), ]
        denied_user = G(User, groups=[denied_groups[0], ])

        unrestricted_event = G(Event)
        G(AttendanceEvent, event=unrestricted_event)
        restricted_event = G(Event)
        G(GroupRestriction, event=restricted_event, groups=allowed_groups)
        G(AttendanceEvent, event=restricted_event)

        self.assertTrue(restricted_event.can_display(allowed_user),
                        "User should be able to view restricted event if in allowed group")
        self.assertFalse(restricted_event.can_display(denied_user),
                         "User should not be able to display event if not in allowed group")
        self.assertTrue(unrestricted_event.can_display(allowed_user),
                        "Any user should be able to see unrestricted events")
        self.assertTrue(unrestricted_event.can_display(denied_user),
                        "Any user should be able to see unrestricted events")

        attend_user_to_event(restricted_event, denied_user)
        self.assertTrue(restricted_event.can_display(denied_user),
                        "User should be able to see event when they are attending even if the event is restricted")


class WaitlistAttendanceEventTest(TestCase):
    def setUp(self):
        self.attendance_event = generate_attendance_event(max_capacity=2)

    def test_changing_max_capacity_with_no_guestlist_should_do_nothing(self):
        for i in range(1):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        self.attendance_event.max_capacity = 4
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_lowering_max_capacity(self):
        for i in range(1):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        self.attendance_event.max_capacity = 1
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_changing_max_capacity_should_notify_waitlist(self):
        for i in range(4):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        self.attendance_event.max_capacity = 3
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_changing_max_capacity_should_notify_waitlist_with_capacity_larger_than_guestlist(self):
        for i in range(4):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        self.attendance_event.max_capacity = 5
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 2)

    def test_changing_reservation_should_notify_waitlist(self):
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        for i in range(4):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        reservation.seats = 1
        reservation.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_changing_reservation_and_max_capacity_should_notify_waitlist(self):
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        for i in range(5):
            generate_attendee(self.attendance_event.event, 'user' + str(i))

        reservation.seats = 1
        reservation.save()
        self.attendance_event.max_capacity = 3
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 2)


class AttendeeModelTest(TestCase):
    def setUp(self):
        self.user = G(
            User, username='ola123', ntnu_username='ola123ntnu',
            first_name="ola", last_name="nordmann"
        )
        self.attendance_event = generate_attendance_event()

    def test_attendee_unicode_is_correct(self):
        attendee = G(Attendee, event=self.attendance_event,
                     user=self.user, attended=False)

        self.assertEqual(attendee.__str__(), self.user.get_full_name())
        self.assertNotEqual(attendee.__str__(), 'Ola Normann')
