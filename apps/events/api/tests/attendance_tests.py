from datetime import UTC, datetime, timedelta
from time import sleep

from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.utils import timezone
from django_dynamic_fixture import G
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase

from apps.events.models import Event
from apps.events.models.Attendance import AttendanceEvent, Attendee
from apps.events.tests.utils import (
    attend_user_to_event,
    generate_event,
    generate_payment,
    generate_user,
    pay_for_event,
)
from apps.marks.models import MarkRuleSet
from apps.notifications.constants import PermissionType
from apps.notifications.models import Permission
from apps.payment.models import PaymentDelay
from onlineweb4.fields.turnstile import mock_validate_turnstile
from onlineweb4.testing import GetUrlMixin

from ...models import Extras, StatusCode
from .utils import generate_attendee

User = settings.AUTH_USER_MODEL


class AttendanceEventTestCase(GetUrlMixin, APITestCase):
    basename = "events_attendance_events"

    def setUp(self):
        self.committee = G(Group, name="Arrkom")
        self.user = generate_user(username="_user")
        self.client.force_authenticate(user=self.user)

        self.captcha_arg = {"turnstile": "dummy"}

        self.event = generate_event(organizer=self.committee)
        self.event.attendance_event.registration_start = timezone.now()
        self.event.attendance_event.registration_end = (
            timezone.now() + timezone.timedelta(days=2)
        )
        self.event.attendance_event.max_capacity = 20
        self.event.attendance_event.save()
        self.attendee1 = generate_attendee(self.event, "test1", "4321")
        self.attendee2 = generate_attendee(self.event, "test2", "1234")
        self.attendees = [self.attendee1, self.attendee2]

    def get_register_url(self, event_id: int):
        return self.get_action_url("register", event_id)

    def get_unregister_url(self, event_id: int):
        return self.get_action_url("unregister", event_id)

    def get_attendee_url(self, event_id: int):
        return self.get_action_url("attendee", event_id)

    def get_public_attendees_url(self, event_id: int):
        return self.get_action_url("public-attendees", event_id)

    def get_extras_url(self, event_id: int):
        return self.get_action_url("extras", event_id)

    def get_payment_url(self, event_id: int):
        return self.get_action_url("payment", event_id)

    def test_anonymous_user_can_get_list(self):
        self.client.force_authenticate(user=None)
        with self.assertNumQueries(10):
            response = self.client.get(self.get_list_url())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_extra_queries_for_logged_in(self):
        with self.assertNumQueries(15):
            response = self.client.get(self.get_list_url())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_get_detail(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_detail_url(self.event.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock_validate_turnstile()
    def test_user_cannot_register_for_a_non_attendance_event(self, _):
        event_without_attendance = generate_event(
            organizer=self.committee, attendance=False
        )

        response = self.client.post(
            self.get_register_url(event_without_attendance.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock_validate_turnstile()
    def test_guest_user_can_register_for_event_with_guest_attendance(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(attendance.is_attendee(self.user))

    @mock_validate_turnstile()
    def test_signup_settings_override_defaults(self, _):
        test_cases: list[tuple[dict[str, bool], dict[str, bool], dict[str, bool]]] = [
            (
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
            ),
            (
                {
                    "show_as_attending_event": False,
                    "allow_pictures": False,
                },
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
            ),
            (
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
                {
                    "show_as_attending_event": False,
                    "allow_pictures": False,
                },
                {
                    "show_as_attending_event": False,
                    "allow_pictures": False,
                },
            ),
            (
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
                {},
                {
                    "show_as_attending_event": True,
                    "allow_pictures": True,
                },
            ),
        ]

        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()
        for user_settings, registration, expected in test_cases:
            with self.subTest():
                privacy = G(
                    "profiles.Privacy",
                    allow_pictures=user_settings["allow_pictures"],
                    visible_as_attending_events=user_settings[
                        "show_as_attending_event"
                    ],
                )
                user = privacy.user
                self.client.force_authenticate(user=user)

                response = self.client.post(
                    self.get_register_url(self.event.id),
                    self.captcha_arg | registration,
                )

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(
                    response.json().get("show_as_attending_event"),
                    expected["show_as_attending_event"],
                )
                self.assertEqual(
                    response.json().get("allow_pictures"),
                    expected["allow_pictures"],
                )

    @mock_validate_turnstile()
    def test_user_can_set_show_as_attending_on_registration(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id),
            {"show_as_attending_event": True, **self.captcha_arg},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json().get("show_as_attending_event"))

    @mock_validate_turnstile()
    def test_allow_pictures_is_set_false_by_default(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.json().get("allow_pictures"))

    @mock_validate_turnstile()
    def test_user_can_set_allow_pictures_on_registration(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id),
            {"allow_pictures": True, **self.captcha_arg},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json().get("allow_pictures"))

    def test_guest_user_cannot_register_with_guest_attendance_without_captcha(self):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(self.get_register_url(self.event.id), {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(attendance.is_attendee(self.user))
        self.assertEqual(response.json().get("turnstile"), ["Dette feltet er påkrevd."])

    @mock_validate_turnstile()
    def test_user_cannot_register_twice(self, _):
        attendance = self.event.attendance_event
        initial_attendees = len(attendance.attendees.all())
        attend_user_to_event(attendance.event, self.user)

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json().get("detail"),
            StatusCode.ALREADY_SIGNED_UP.message,
        )
        self.assertEqual(len(attendance.attendees.all()), initial_attendees + 1)

    @mock_validate_turnstile()
    def test_guest_user_cannot_register_for_event_without_guest_attendance(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = False
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json().get("detail"),
            StatusCode.NOT_A_MEMBER.message,
        )

    @mock_validate_turnstile()
    def test_user_cannot_register_event_after_registration_end(self, _):
        attendance = self.event.attendance_event
        attendance.registration_start = timezone.now() - timezone.timedelta(days=2)
        attendance.registration_end = timezone.now() - timezone.timedelta(days=2)
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json().get("detail"), "Påmeldingen er ikke lenger åpen."
        )

    def test_user_can_unregister_before_deadline(self):
        self.event.attendance_event.unattend_deadline = (
            timezone.now() + timezone.timedelta(days=2)
        )
        self.event.event_start = timezone.now() + timezone.timedelta(days=3)
        self.event.attendance_event.save()
        self.event.save()
        attend_user_to_event(self.event, self.user)

        response = self.client.delete(
            self.get_unregister_url(self.event.id), {"cause": "other"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.event.attendance_event.is_attendee(self.user))

    def test_user_can_unregister_no_cause_fails(self):
        self.event.attendance_event.unattend_deadline = (
            timezone.now() + timezone.timedelta(days=2)
        )
        self.event.event_start = timezone.now() + timezone.timedelta(days=3)
        self.event.attendance_event.save()
        self.event.save()
        attend_user_to_event(self.event, self.user)

        response = self.client.delete(
            self.get_unregister_url(self.event.id), dict(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_unregister_after_deadline_has_passed(self):
        self.event.attendance_event.unattend_deadline = (
            timezone.now() - timezone.timedelta(days=2)
        )
        self.event.attendance_event.save()
        attend_user_to_event(self.event, self.user)

        response = self.client.delete(
            self.get_unregister_url(self.event.id), {"cause": "other"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.event.attendance_event.is_attendee(self.user))
        self.assertEqual(
            response.json().get("detail"),
            "Avmeldingsfristen har gått ut, det er ikke lenger mulig å melde seg av arrangementet.",
        )

    def test_user_cannot_unregister_after_event_has_started(self):
        self.event.attendance_event.unattend_deadline = (
            timezone.now() + timezone.timedelta(days=2)
        )
        self.event.event_start = timezone.now() - timezone.timedelta(hours=1)
        self.event.attendance_event.save()
        self.event.save()
        attend_user_to_event(self.event, self.user)

        response = self.client.delete(
            self.get_unregister_url(self.event.id), {"cause": "other"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.event.attendance_event.is_attendee(self.user))
        self.assertEqual(
            response.json().get("detail"),
            "Du kan ikke melde deg av et arrangement som allerede har startet.",
        )

    @mock_validate_turnstile()
    def test_user_can_re_register_for_an_event_after_unregistering(self, _):
        attend_user_to_event(self.event, self.user)
        self.event.attendance_event.unattend_deadline = (
            timezone.now() + timezone.timedelta(days=2)
        )
        self.event.attendance_event.guest_attendance = True
        self.event.event_start = timezone.now() + timezone.timedelta(days=3)
        self.event.attendance_event.save()
        self.event.save()
        self.client.delete(
            self.get_unregister_url(self.event.id), {"cause": "other"}, format="json"
        )

        response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock_validate_turnstile()
    def test_payment_is_configured_on_registration(self, _):
        generate_payment(
            self.event,
            payment_type=1,
            deadline=timezone.now() + timezone.timedelta(days=1),
        )
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        register_response = self.client.post(
            self.get_register_url(self.event.id), self.captcha_arg
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(register_response.json().get("has_paid"))

        pay_for_event(self.event, self.user)

        attendee_response = self.client.get(self.get_attendee_url(self.event.id))

        self.assertEqual(attendee_response.status_code, status.HTTP_200_OK)
        self.assertTrue(attendee_response.json().get("has_paid"))

    def test_public_attendees_list_works(self):
        self.attendee1.show_as_attending_event = True
        self.attendee2.show_as_attending_event = False
        self.attendee1.save()
        self.attendee2.save()

        with self.assertNumQueries(3):
            response = self.client.get(self.get_public_attendees_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attendee1_data = [
            x for x in response.json() if x.get("id") == self.attendee1.id
        ][0]
        attendee2_data = [
            x for x in response.json() if x.get("id") == self.attendee2.id
        ][0]
        self.assertEqual(attendee1_data.get("is_visible"), True)
        self.assertEqual(
            attendee1_data.get("full_name"), self.attendee1.user.get_full_name()
        )
        self.assertEqual(attendee2_data.get("is_visible"), False)
        self.assertNotEqual(
            attendee2_data.get("full_name"), self.attendee2.user.get_full_name()
        )

    def test_public_attendees_list_only_works_for_authenticated_users(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_public_attendees_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_attendance_payment_info_works_when_event_has_payment(self):
        generate_payment(
            self.event,
            payment_type=1,
            deadline=timezone.now() + timezone.timedelta(days=1),
        )
        response = self.client.get(self.get_payment_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attendance_payment_info_fail_on_event_without_payment(self):
        response = self.client.get(self.get_payment_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_attendance_payment_info_only_works_for_authenticated_users(self):
        self.client.force_authenticate(user=None)
        generate_payment(
            self.event,
            payment_type=1,
            deadline=timezone.now() + timezone.timedelta(days=1),
        )
        response = self.client.get(self.get_payment_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get_extras(self):
        self.event.attendance_event.extras.add(G(Extras))
        self.event.attendance_event.extras.add(G(Extras))
        response = self.client.get(self.get_extras_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_extras_only_works_for_authenticated_users(self):
        self.client.force_authenticate(user=None)
        self.event.attendance_event.extras.add(G(Extras))
        self.event.attendance_event.extras.add(G(Extras))
        response = self.client.get(self.get_extras_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# This needs to be a TransactionTestCase since notifications are sent using on_commit hooks
# see https://docs.djangoproject.com/en/5.1/topics/testing/tools/#django.test.TransactionTestCase
class EventsUnattendWaitList(GetUrlMixin, APITransactionTestCase):
    basename = "events_attendance_events"

    def setUp(self):
        G(Permission, permission_type=PermissionType.WAIT_LIST_BUMP, force_email=True)
        self.event = G(Event, event_start=timezone.now() + timedelta(days=1))
        G(
            AttendanceEvent,
            event=self.event,
            unattend_deadline=timezone.now() + timedelta(days=1),
            max_capacity=2,
            waitlist=True,
        )
        self.user = generate_user("test")
        self.client.force_login(self.user)
        self.other_user = generate_user("other")
        self.url = self.get_action_url("unregister", self.event.id)
        self.rule_Set = G(
            MarkRuleSet,
            duration=timedelta(days=14),
            valid_from_date=datetime(year=2016, month=1, day=1, tzinfo=UTC),
        )

    def test_unattend_notifies_waitlist_when_attending(self):
        G(Attendee, event=self.event.attendance_event)
        attend_user_to_event(self.event, self.user)
        G(Attendee, event=self.event.attendance_event, n=3)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Du har fått plass på", mail.outbox[0].subject)

    def test_unattend_does_not_notify_waitlist_when_on_waitlist(self):
        G(Attendee, event=self.event.attendance_event, n=2)
        attend_user_to_event(self.event, self.user)
        G(Attendee, event=self.event.attendance_event)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        sleep(2)
        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2017-01-01 12:00")
    def test_payment_type_instant_uses_extended(self):
        generate_payment(self.event, payment_type=1)
        G(Attendee, event=self.event.attendance_event)
        attend_user_to_event(self.event, self.user)
        attend_user_to_event(self.event, self.other_user)
        G(Attendee, event=self.event.attendance_event)
        payment_delay_time = timedelta(days=2)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        sleep(2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Du har fått plass på", mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)

    def test_payment_delay_is_not_created_if_deadline_over_48_hours(self):
        generate_payment(
            self.event, payment_type=2, deadline=timezone.now() + timedelta(days=3)
        )
        G(Attendee, event=self.event.attendance_event)
        attend_user_to_event(self.event, self.user)
        attend_user_to_event(self.event, self.other_user)
        G(Attendee, event=self.event.attendance_event)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        sleep(2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Du har fått plass på", mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.filter(user=self.other_user)
        self.assertFalse(payment_delay.exists())

    @freeze_time("2017-01-01 12:00")
    def test_payment_delay_is_created_if_deadline_under_48_hours(self):
        generate_payment(
            self.event, payment_type=2, deadline=timezone.now() + timedelta(hours=47)
        )
        G(Attendee, event=self.event.attendance_event)
        attend_user_to_event(self.event, self.user)
        other_user_attendee = attend_user_to_event(self.event, self.other_user)
        G(Attendee, event=self.event.attendance_event)
        payment_delay_time = timedelta(days=2)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertIn(
            other_user_attendee, self.event.attendance_event.attending_attendees_qs
        )
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        sleep(2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Du har fått plass på", mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)

    @freeze_time("2017-01-01 12:00")
    def test_payment_type_delay_uses_payment_delay(self):
        delay_days = 4
        payment_delay_time = timedelta(days=delay_days)
        generate_payment(self.event, payment_type=3, delay=payment_delay_time)
        G(Attendee, event=self.event.attendance_event)
        attend_user_to_event(self.event, self.user)
        attend_user_to_event(self.event, self.other_user)
        G(Attendee, event=self.event.attendance_event)

        r = self.client.delete(self.url, {"cause": "other"}, format="json")

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        sleep(2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Du har fått plass på", mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)
