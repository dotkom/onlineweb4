# -*- coding: utf-8 -*-

import datetime
import logging
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import AllowedUsername
from apps.events.models import (AttendanceEvent, Attendee, Event, FieldOfStudyRule, GradeRule,
                                GroupRestriction, Reservation, Reservee, RuleBundle, UserGroupRule)
from apps.events.mommy import SetEventMarks
from apps.marks.models import DURATION, Mark, MarkUser


def create_generic_event():
        future = timezone.now() + datetime.timedelta(days=1)
        event_start = future
        event_end = future + datetime.timedelta(days=1)
        event = G(Event, event_start=event_start, event_end=event_end)

        return event


class EventTest(TestCase):

    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(AttendanceEvent, event=self.event, max_capacity=2)
        self.user = G(User, username='ola123', ntnu_username='ola123ntnu', first_name="ola", last_name="nordmann")
        self.attendee = G(Attendee, event=self.attendance_event, user=self.user)
        self.logger = logging.getLogger(__name__)
        # Setting registration start 1 hour in the past, end one week in the future.
        self.now = timezone.now()
        self.attendance_event.registration_start = self.now - datetime.timedelta(hours=1)
        self.attendance_event.registration_end = self.now + datetime.timedelta(days=7)
        # Making the user a member.
        self.allowed_username = G(AllowedUsername, username='ola123ntnu',
                                  expiration_date=self.now + datetime.timedelta(weeks=1))

    def testEventUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on Event with dynamic fixtures")
        self.assertEqual(self.event.__str__(), 'Sjakkturnering')

    def testAttendanceEventUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on AttendanceEvent with dynamic fixtures")
        self.assertEqual(self.attendance_event.__str__(), 'Sjakkturnering')

    #
    # Event attendees, seats and wait list
    #

    def testAttendeeAndWaitlistQS(self):
        self.logger.debug("Testing attendee queryset")
        user1 = G(User, username="jan", first_name="jan")
        G(Attendee, event=self.attendance_event, user=user1)
        user2 = G(User, username="per", first_name="per")
        G(Attendee, event=self.attendance_event, user=user2)
        user3 = G(User, username="gro", first_name="gro")
        G(Attendee, event=self.attendance_event, user=user3)
        self.assertEqual(self.attendance_event.max_capacity, 2)
        self.assertEqual(self.attendance_event.number_of_attendees, 2)
        self.assertEqual(self.attendance_event.number_on_waitlist, 2)

    def testReservedSeats(self):
        self.logger.debug("Testing reserved seats")
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        G(Reservee, reservation=reservation, name="jan", note="jan er kul", allergies="allergi1")
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 1)
        G(Reservee, reservation=reservation, name="per", note="per er rå", allergies="allergi2")
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 2)

    def testNumberOfTakenSeats(self):
        # Increase event capacity so we have more room to test with
        self.attendance_event.max_capacity = 5
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        # Make a reservation, for 2 seats
        reservation = G(Reservation, attendance_event=self.attendance_event, seats=2)
        G(Reservee, reservation=reservation, name="jan", note="jan er kul", allergies="allergi1")
        self.assertEqual(self.attendance_event.max_capacity, 5)
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 1)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        G(Reservee, reservation=reservation, name="per", note="per er rå", allergies="allergi2")
        self.assertEqual(self.attendance_event.number_of_attendees, 1)
        self.assertEqual(self.attendance_event.number_of_reserved_seats_taken, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 3)
        user3 = G(User, username="gro", first_name="gro")
        G(Attendee, event=self.attendance_event, user=user3)
        self.assertEqual(self.attendance_event.number_of_attendees, 2)
        self.assertEqual(self.attendance_event.number_of_seats_taken, 4)

    #
    # Rule Bundles
    #

    def testAttendeeUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on Attendee with dynamic fixtures")
        self.assertEqual(self.attendee.__str__(), self.user.get_full_name())
        self.assertNotEqual(self.attendee.__str__(), 'Ola Normann')

    def testSignUpWithNoRulesNoMarks(self):
        self.logger.debug("Testing signup with no rules and no marks.")

        # The user should be able to attend now, since the event has no rule bundles.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertTrue(response['status'])
        self.assertEqual(200, response['status_code'])

    def testSignUpWithNoRulesNoMarksNoMembership(self):
        self.logger.debug("Testing signup with no rules, no marks and user not member.")

        self.allowed_username.delete()
        # The user should not be able to attend, since the event has no rule bundles
        # and they are not a member.
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(400, response['status_code'])

    def testSignUpWithNoRulesAndAMark(self):
        self.logger.debug("Testing signup with no rules and a mark.")

        # Giving the user a mark to see if the status goes to False.
        mark1 = G(Mark, title='Testprikk12345')
        G(MarkUser, user=self.user, mark=mark1, expiration_date=self.now+datetime.timedelta(days=DURATION))
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(401, response['status_code'])

    def testFieldOfStudyRule(self):
        self.logger.debug("Testing restriction with field of study rules.")

        # Create the rule and rule_bundles
        self.fosrule = G(FieldOfStudyRule, field_of_study=1, offset=24)
        self.assertEqual(self.fosrule.field_of_study, 1)
        self.assertEqual(self.fosrule.offset, 24)
        self.assertEqual(str(self.fosrule), "Bachelor i Informatikk etter 24 timer")
        self.rulebundle = G(RuleBundle, description='')
        self.rulebundle.field_of_study_rules.add(self.fosrule)
        self.assertEqual(str(self.rulebundle), "Bachelor i Informatikk etter 24 timer")
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
        self.logger.debug("Testing restriction with grade rules.")

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
        self.logger.debug("Testing restriction with group rules.")

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
        self.logger.debug("Testing restriction with group rules.")

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
        self.attendance_event.registration_start = self.now + datetime.timedelta(hours=1)
        response = self.attendance_event.is_eligible_for_signup(self.user)
        self.assertFalse(response['status'])
        self.assertEqual(402, response['status_code'])

    #
    # Mommy Attandance mark tests
    #

    def testMommyNotAttended(self):
        self.attendee.attended = False
        self.attendee.save()
        self.assertEqual([self.user], self.attendance_event.not_attended())

    def testMommyAttended(self):
        self.attendee.attended = True
        self.attendee.save()
        self.assertEqual([], self.attendance_event.not_attended())

    def testMommyActiveEvents(self):
        self.attendance_event.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.event.save()

        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.attendance_event.save()

        self.assertEqual(self.attendance_event, SetEventMarks.active_events()[0])

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
        self.attendee.attended = False
        self.attendee.save()
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        SetEventMarks.setMarks(self.attendance_event)

        self.assertTrue(self.attendance_event.marks_has_been_set)
        self.assertEqual(self.user, MarkUser.objects.get().user)

    def testMommyEveryoneAttendend(self):
        self.attendee.attended = True
        self.attendee.save()
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        SetEventMarks.setMarks(self.attendance_event)

        self.assertTrue(self.attendance_event.marks_has_been_set)
        self.assertFalse(MarkUser.objects.all())

    def testMommyGenerateEmptyMessage(self):
        self.attendee.attended = True
        self.attendee.save()
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        message = SetEventMarks.generate_message(self.attendance_event)

        self.assertFalse(message.send)
        self.assertFalse(message.results_message)

    def testMommyGenerateMessage(self):
        self.attendee.attended = False
        self.attendee.save()
        self.attendance_event.marks_has_been_set = False
        self.attendance_event.automatically_set_marks = True
        self.event.event_end = timezone.now() - datetime.timedelta(days=1)
        self.attendance_event.save()
        self.event.save()

        message = SetEventMarks.generate_message(self.attendance_event)

        self.assertTrue(message.send)
        self.assertTrue(message.committee_message)

    def testRestrictedEvents(self):
        allowed_groups = [G(Group), G(Group)]
        allowed_user = G(User, groups=[allowed_groups[0], ])

        denied_groups = [G(Group), ]
        denied_user = G(User, groups=[denied_groups[0], ])

        unrestricted_event = G(Event)
        restricted_event = G(Event)
        G(GroupRestriction, event=restricted_event, groups=allowed_groups)
        # restricted_event.group_restriction.add(allowed_groups)

        self.assertTrue(restricted_event.can_display(allowed_user),
                        "User should be able to view restricted event if in allowed group")
        self.assertFalse(restricted_event.can_display(denied_user),
                         "User should not be able to display event if not in allowed group")
        self.assertTrue(unrestricted_event.can_display(allowed_user),
                        "Any user should be able to see unrestricted events")
        self.assertTrue(unrestricted_event.can_display(denied_user),
                        "Any user should be able to see unrestricted events")

    def test_no_error_if_already_signed_up(self):
        user = G(User)

        self.client.force_login(user)

        event = G(Event)
        event.attendance_event = G(AttendanceEvent,
                                   event=event, guest_attendance=True, max_capacity=2,
                                   registration_start=timezone.now() - datetime.timedelta(hours=1),
                                   registration_end=timezone.now() + datetime.timedelta(hours=1))

        os.environ['RECAPTCHA_TESTING'] = 'True'

        form_fields = {
            'g-recaptcha-response': 'PASSED',
            'phone_number': '12345678',
            'note': 'hello',
            'mark_rules': True,
        }

        url = reverse('attend_event', kwargs={'event_id': event.id})

        self.client.post(url, form_fields)

        self.assertEqual(1, Attendee.objects.filter(event=event.attendance_event, user=user).count())

        self.client.post(url, form_fields)

        del os.environ['RECAPTCHA_TESTING']


class EventOrderedByRegistrationTestCase(TestCase):
    def setUp(self):
        self.FEATURED_TIMEDELTA_SETTINGS = settings
        # Override settings so that the tests will work even if we update the default delta
        self.FEATURED_TIMEDELTA_SETTINGS.OW4_SETTINGS['events']['OW4_EVENTS_FEATURED_DAYS_FUTURE'] = 7
        self.FEATURED_TIMEDELTA_SETTINGS.OW4_SETTINGS['events']['OW4_EVENTS_FEATURED_DAYS_PAST'] = 7

    def test_registration_no_push_forward(self):
        """
        Tests that an AttendanceEvent with registration date far in the future is sorted by its event end date,
        like any other event.
        """
        today = timezone.now()
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five)
        G(AttendanceEvent, registration_start=month_ahead_plus_five, registration_end=month_ahead_plus_five,
          event=pushed_event)

        expected_order = [normal_event, pushed_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)

    def test_registration_start_pushed_forward(self):
        """
        Tests that an AttendanceEvent with registration date within the "featured delta" (+/- 7 days from today)
        will be pushed ahead in the event list, thus sorted by registration start rather than event end.
        """
        today = timezone.now()
        three_days_ahead = today + datetime.timedelta(days=3)
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five)
        G(AttendanceEvent, registration_start=three_days_ahead, registration_end=three_days_ahead, event=pushed_event)

        expected_order = [pushed_event, normal_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)

    def test_registration_past_push_forward(self):
        """
        Tests that an AttendanceEvent with a registration date in the past, outside the "featured delta" (+/- 7 days)
        will be sorted by the event's end date.
        """
        today = timezone.now()
        month_ahead = today + datetime.timedelta(days=30)
        month_ahead_plus_five = month_ahead + datetime.timedelta(days=5)
        month_back = today - datetime.timedelta(days=30)
        normal_event = G(Event, event_start=month_ahead, event_end=month_ahead)
        pushed_event = G(Event, event_start=month_ahead_plus_five, event_end=month_ahead_plus_five)
        G(AttendanceEvent, registration_start=month_back, registration_end=month_back, event=pushed_event)

        expected_order = [normal_event, pushed_event]

        with override_settings(settings=self.FEATURED_TIMEDELTA_SETTINGS):
            self.assertEqual(list(Event.by_registration.all()), expected_order)


class EventsURLTestCase(TestCase):
    def test_events_index_empty(self):
        url = reverse('events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_index_exists(self):
        create_generic_event()

        url = reverse('events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):
        event = create_generic_event()

        url = reverse('events_details', args=(event.id, event.slug))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_events(self):
        query = ''

        _url_pre_get_param = reverse('search_events')
        url = _url_pre_get_param + '?query=%s' % query

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_ics_all(self):
        url = reverse('events_ics')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_ics_specific_event(self):
        event = create_generic_event()

        url = reverse('event_ics', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventsAPIURLTestCase(APITestCase):
    def test_events_list_empty(self):
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_list_exists(self):
        create_generic_event()
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):
        event = create_generic_event()
        url = reverse('events-detail', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
