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
from apps.events.models import (
    AttendanceEvent,
    Attendee,
    CompanyEvent,
    Event,
    FieldOfStudyRule,
    GradeRule,
    GroupRestriction,
    Reservation,
    Reservee,
    RuleBundle,
    UserGroupRule,
)
from apps.feedback.models import Feedback, FeedbackRelation
from apps.marks.models import DURATION, Mark, MarkUser
from apps.notifications.constants import PermissionType
from apps.notifications.models import Permission

from .utils import attend_user_to_event, generate_attendance_event, generate_attendee


class EventModelTest(TestCase):
    def test_event_unicode(self):
        event = G(Event, title="Sjakkturnering")

        self.assertEqual(event.__str__(), "Sjakkturnering")

    def test_company_event_method_returns_company_events(self):
        event = G(Event, title="Sjakkturnering")
        company1 = G(CompanyEvent, event=event, company=G(Company))
        company2 = G(CompanyEvent, event=event, company=G(Company))

        companies = event.company_event

        self.assertIn(company1, companies)
        self.assertIn(company2, companies)


class AttendanceEventModelTest(TestCase):
    def setUp(self):
        self.event: Event = G(Event, title="Sjakkturnering")
        self.attendance_event: AttendanceEvent = G(
            AttendanceEvent, event=self.event, max_capacity=2
        )
        self.user: User = G(
            User,
            username="ola123",
            ntnu_username="ola123ntnu",
            first_name="ola",
            last_name="nordmann",
        )
        # Setting registration start 1 hour in the past, end one week in the future.
        self.now = timezone.now()
        self.attendance_event.registration_start = self.now - datetime.timedelta(
            hours=1
        )
        self.attendance_event.registration_end = self.now + datetime.timedelta(days=7)
        # Making the user a member.
        self.allowed_username: AllowedUsername = G(
            AllowedUsername,
            username="ola123ntnu",
            expiration_date=self.now + datetime.timedelta(weeks=1),
        )

    def create_attendance_event(self):
        event: Event = G(Event)
        return G(AttendanceEvent, event=event)

    def add_feedback(self, attendance_event: AttendanceEvent) -> FeedbackRelation:
        feedback: Feedback = G(Feedback)
        return G(
            FeedbackRelation,
            feedback=feedback,
            object_id=attendance_event.event_id,
            content_type=ContentType.objects.get_for_model(Event),
        )

    def add_reservation(self, attendance_event: AttendanceEvent) -> Reservation:
        return G(Reservation, attendance_event=attendance_event)

    def test_attendance_event_unicode_is_correct(self):
        self.assertEqual(self.attendance_event.__str__(), "Sjakkturnering")

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
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        G(
            Reservee,
            reservation=reservation,
            name="jan",
            note="jan er kul",
            allergies="allergi1",
        )
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 1)
        G(
            Reservee,
            reservation=reservation,
            name="per",
            note="per er rå",
            allergies="allergi2",
        )
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 2)

    def test_number_of_taken_seats(self):
        G(Attendee, event=self.attendance_event, user=self.user, attended=False)
        # Increase event capacity so we have more room to test with
        self.attendance_event.max_capacity = 5
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        # Make a reservation, for 2 seats
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        G(
            Reservee,
            reservation=reservation,
            name="jan",
            note="jan er kul",
            allergies="allergi1",
        )
        self.assertEqual(self.attendance_event.max_capacity, 5)
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 1)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        G(
            Reservee,
            reservation=reservation,
            name="per",
            note="per er rå",
            allergies="allergi2",
        )
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        user3 = G(User, username="gro", first_name="gro")
        G(Attendee, event=self.attendance_event, user=user3)
        self.assertEqual(self.attendance_event.number_of_attendees, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 4)

    def test_sign_up_with_no_rules_no_marks(self):
        # The user should be able to attend now, since the event has no rule bundles.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(200, response["status_code"])

    def test_sign_up_with_no_rules_no_marks_no_membership(self):
        self.allowed_username.delete()
        # The user should not be able to attend, since the event has no rule bundles
        # and they are not a member.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(400, response["status_code"])

    def test_sign_up_with_no_rules_and_a_mark(self):
        # Giving the user a mark to see if the status goes to False.
        mark1 = G(Mark, title="Testprikk12345")
        G(
            MarkUser,
            user=self.user,
            mark=mark1,
            expiration_date=self.now + datetime.timedelta(days=DURATION),
        )
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(401, response["status_code"])

    def test_field_of_study_rule(self):
        # Create the rule and rule_bundles
        self.fos_rule = G(FieldOfStudyRule, field_of_study=1, offset=24)
        self.assertEqual(self.fos_rule.field_of_study, 1)
        self.assertEqual(self.fos_rule.offset, 24)
        self.assertEqual(str(self.fos_rule), "Bachelor i Informatikk etter 24 timer")
        self.rule_bundle = G(RuleBundle, description="")
        self.rule_bundle.field_of_study_rules.add(self.fos_rule)
        self.assertEqual(str(self.rule_bundle), "Bachelor i Informatikk etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rule_bundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(410, response["status_code"])

        # Make the user a bachelor and try again. Should get message about offset.
        self.user.field_of_study = 1
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(420, response["status_code"])

        # Add a new grade rule with no offset and see if signup works
        self.fos_rule2 = G(FieldOfStudyRule, field_of_study=1, offset=0)
        self.rule_bundle.field_of_study_rules.add(self.fos_rule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(210, response["status_code"])

    def test_grade_rule(self):
        # Create the rule and rule_bundles
        self.graderule = G(GradeRule, grade=1, offset=24)
        self.assertEqual(self.graderule.grade, 1)
        self.assertEqual(self.graderule.offset, 24)
        self.assertEqual(str(self.graderule), "1. klasse etter 24 timer")
        self.rule_bundle = G(RuleBundle, description="")
        self.rule_bundle.grade_rules.add(self.graderule)
        self.assertEqual(str(self.rule_bundle), "1. klasse etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rule_bundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(411, response["status_code"])

        # Make the user a grade 1 and try again. Should get message about offset.
        self.user.field_of_study = 1
        self.user.started_date = self.now.date()
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(421, response["status_code"])

        # Add a new grade rule with no offset and see if signup works
        self.graderule2 = G(GradeRule, grade=1, offset=0)
        self.rule_bundle.grade_rules.add(self.graderule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(211, response["status_code"])

    def test_user_group_rule(self):
        # Create the rule and rule_bundles
        self.group = G(Group, name="Testgroup")
        self.group_rule = G(UserGroupRule, group=self.group, offset=24)
        self.assertEqual(self.group_rule.group, self.group)
        self.assertEqual(self.group_rule.offset, 24)
        self.assertEqual(str(self.group_rule), "Testgroup etter 24 timer")
        self.rule_bundle = G(RuleBundle, description="")
        self.rule_bundle.user_group_rules.add(self.group_rule)
        self.assertEqual(str(self.rule_bundle), "Testgroup etter 24 timer")
        self.attendance_event.rule_bundles.add(self.rule_bundle)

        # Status should be negative, and indicate that the restriction is a grade rule
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(412, response["status_code"])

        # Make the user a grade 1 and try again. Should get message about offset
        self.user.groups.add(self.group)
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(422, response["status_code"])

        # Add a new grade rule with no offset and see if signup works
        self.grouprule2 = G(UserGroupRule, group=self.group, offset=0)
        self.rule_bundle.user_group_rules.add(self.grouprule2)

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(212, response["status_code"])

    def test_rule_offset_and_mark_offset(self):
        group: Group = G(Group, name="Testgroup")
        group_rule: GradeRule = G(UserGroupRule, group=group, offset=24)
        rule_bundle: RuleBundle = G(RuleBundle, description="")
        rule_bundle.user_group_rules.add(group_rule)
        self.attendance_event.rule_bundles.add(rule_bundle)
        # Registration just opened
        self.attendance_event.registration_start = timezone.now() - timezone.timedelta(
            minutes=1
        )

        # User should not be able to register because of the group rule offset
        self.user.groups.add(group)
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(422, response["status_code"])

        # Simulate a day passing for the offset to not have an effect anymore
        self.attendance_event.registration_start -= timezone.timedelta(hours=24)
        self.attendance_event.save()

        # User should be able to register for event since offset has passed
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(212, response["status_code"])

        mark: Mark = G(Mark, title="Test mark")
        G(
            MarkUser,
            user=self.user,
            mark=mark,
            expiration_date=self.now + datetime.timedelta(days=DURATION),
        )

        # User should not be eligible for signup anymore because they have a mark
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(401, response["status_code"])

        # Set registration to be as far into the past as both the offset from the rule and the mark
        self.attendance_event.registration_start -= timezone.timedelta(hours=24)
        self.attendance_event.save()

        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response["status"])
        self.assertEqual(212, response["status_code"])

    def test_future_access_trumps_offset(self):
        # Create two different rules, and verify that the response is false, but without offset
        # Group rule
        self.group = G(Group, name="Testgroup")
        self.group_rule = G(UserGroupRule, group=self.group, offset=0)
        self.user.groups.add(self.group)
        # Grade rule
        self.graderule = G(GradeRule, grade=1, offset=24)
        self.user.field_of_study = 1
        self.user.started_date = self.now.date()
        # Make the rule bundle
        self.rule_bundle = G(RuleBundle, description="")
        self.rule_bundle.grade_rules.add(self.graderule)
        self.rule_bundle.user_group_rules.add(self.group_rule)
        self.attendance_event.rule_bundles.add(self.rule_bundle)
        # Move registration start into the future
        self.attendance_event.registration_start = self.now + datetime.timedelta(
            hours=1
        )
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response["status"])
        self.assertEqual(402, response["status_code"])

    def test_restricted_events(self):
        allowed_groups = [G(Group), G(Group)]
        allowed_user = G(User, groups=[allowed_groups[0]])

        denied_groups = [G(Group)]
        denied_user = G(User, groups=[denied_groups[0]])

        unrestricted_event = G(Event)
        G(AttendanceEvent, event=unrestricted_event)
        restricted_event = G(Event)
        G(GroupRestriction, event=restricted_event, groups=allowed_groups)
        G(AttendanceEvent, event=restricted_event)

        self.assertTrue(
            restricted_event.can_display(allowed_user),
            "User should be able to view restricted event if in allowed group",
        )
        self.assertFalse(
            restricted_event.can_display(denied_user),
            "User should not be able to display event if not in allowed group",
        )
        self.assertTrue(
            unrestricted_event.can_display(allowed_user),
            "Any user should be able to see unrestricted events",
        )
        self.assertTrue(
            unrestricted_event.can_display(denied_user),
            "Any user should be able to see unrestricted events",
        )

        attend_user_to_event(restricted_event, denied_user)
        self.assertTrue(
            restricted_event.can_display(denied_user),
            "User should be able to see event when they are attending even if the event is restricted",
        )


class WaitlistAttendanceEventTest(TestCase):
    def setUp(self):
        self.attendance_event = generate_attendance_event(max_capacity=2)

    def test_changing_max_capacity_with_no_guestlist_should_do_nothing(self):
        for i in range(1):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        self.attendance_event.max_capacity = 4
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_lowering_max_capacity(self):
        for i in range(1):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        self.attendance_event.max_capacity = 1
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_changing_max_capacity_should_notify_waitlist(self):
        G(Permission, permission_type=PermissionType.WAIT_LIST_BUMP, force_email=True)
        for i in range(4):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        self.attendance_event.max_capacity = 3
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_changing_max_capacity_should_notify_waitlist_with_capacity_larger_than_guestlist(
        self,
    ):
        G(Permission, permission_type=PermissionType.WAIT_LIST_BUMP, force_email=True)
        for i in range(4):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        self.attendance_event.max_capacity = 5
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 2)

    def test_changing_reservation_should_notify_waitlist(self):
        G(Permission, permission_type=PermissionType.WAIT_LIST_BUMP, force_email=True)
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        for i in range(4):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        reservation.seats = 1
        reservation.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_changing_reservation_and_max_capacity_should_notify_waitlist(self):
        G(Permission, permission_type=PermissionType.WAIT_LIST_BUMP, force_email=True)
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        for i in range(5):
            generate_attendee(self.attendance_event.event, "user" + str(i))

        reservation.seats = 1
        reservation.save()
        self.attendance_event.max_capacity = 3
        self.attendance_event.save()

        self.assertEqual(len(mail.outbox), 2)


class AttendeeModelTest(TestCase):
    def setUp(self):
        self.user = G(
            User,
            username="ola123",
            ntnu_username="ola123ntnu",
            first_name="ola",
            last_name="nordmann",
        )
        self.attendance_event = generate_attendance_event()

    def test_attendee_unicode_is_correct(self):
        attendee = G(
            Attendee, event=self.attendance_event, user=self.user, attended=False
        )

        self.assertEqual(attendee.__str__(), self.user.get_full_name())
        self.assertNotEqual(attendee.__str__(), "Ola Normann")
