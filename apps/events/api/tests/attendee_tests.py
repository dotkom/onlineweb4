from django.contrib.auth.models import Group
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm
from rest_framework import status

from apps.authentication.models import OnlineUser
from apps.events.constants import AttendStatus
from apps.events.tests.utils import attend_user_to_event, generate_event
from apps.online_oidc_provider.test import OIDCTestCase

from .utils import generate_attendee, generate_valid_rfid


class AttendeeTestCase(OIDCTestCase):
    basename = "events_attendees"

    def setUp(self):
        self.committee: Group = G(Group, name="Arrkom")
        assign_perm("events.change_attendee", self.committee)
        self.user.groups.add(self.committee)

        self.event = generate_event(organizer=self.committee)
        self.attendee1 = generate_attendee(self.event, "test1", "0123")
        self.attendee2 = generate_attendee(self.event, "test2", "3210")
        self.attendees = [self.attendee1, self.attendee2]

    def get_register_attendance_url(self):
        return self.get_action_url("register-attendance")

    def get_administrate_url(self, attendee_id: int):
        return self.get_action_url("administrate", attendee_id)

    def get_change_url(self, attendee_id: int):
        return self.get_action_url("change", attendee_id)

    def refresh_attendees(self):
        for attendee in self.attendees:
            attendee.refresh_from_db()
            attendee.user.refresh_from_db()

    def test_admin_can_administrate_other_attendee(self):
        self.attendee1.paid = False
        self.attendee1.save()

        response = self.client.patch(
            self.get_administrate_url(self.attendee1.id), {"paid": True}, **self.headers
        )
        self.attendee1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("paid"), True)
        self.assertEqual(self.attendee1.paid, True)

    def test_admin_can_administrate_their_own_attendee(self):
        attendee = attend_user_to_event(self.event, self.user)
        attendee.paid = False
        attendee.save()

        response = self.client.patch(
            self.get_administrate_url(self.attendee1.id), {"paid": True}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("paid"), True)

    def test_non_admin_cannot_administrate_their_own_attendee(self):
        self.user.groups.remove(self.committee)
        attendee = attend_user_to_event(self.event, self.user)
        attendee.paid = False
        attendee.save()

        response = self.client.patch(
            self.get_administrate_url(self.attendee1.id), {"paid": True}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_change_consent(self):
        self.attendee1.show_as_attending_event = False
        self.attendee1.save()

        response = self.client.patch(
            self.get_administrate_url(self.attendee1.id),
            {"show_as_attending_event": True},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("show_as_attending_event"), False)

    def test_admin_cannot_change_other_user(self):
        self.attendee1.show_as_attending_event = False
        self.attendee1.save()

        response = self.client.patch(
            self.get_change_url(self.attendee1.id),
            {"show_as_attending_event": True},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_change_own_attendee(self):
        attendee = attend_user_to_event(self.event, self.user)
        attendee.show_as_attending_event = False
        attendee.save()

        response = self.client.patch(
            self.get_change_url(attendee.id),
            {"show_as_attending_event": True},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("show_as_attending_event"), True)

    def test_missing_auth_returns_unauthorized(self):
        response = self.client.post(self.get_register_attendance_url())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_data_returns_bad_request(self):
        response = self.client.post(self.get_register_attendance_url(), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attend_with_username(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "username": self.attendee1.user.username},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.attendee1.attended)
        self.assertFalse(self.attendee2.attended)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.REGISTER_SUCCESS,
        )

    def test_attend_with_rfid(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": self.attendee1.user.rfid},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.attendee1.attended)
        self.assertFalse(self.attendee2.attended)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.REGISTER_SUCCESS,
        )

    def test_attend_twice(self):
        self.attendee1.attended = True
        self.attendee1.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": self.attendee1.user.rfid},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.PREVIOUSLY_REGISTERED,
        )

    def test_unknown_rfid(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": "fake_rfid"},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.RFID_DOES_NOT_EXIST,
        )

    def test_saves_rfid(self):

        response = self.client.post(
            self.get_register_attendance_url(),
            {
                "event": self.event.id,
                "username": self.attendee1.user.username,
                "rfid": "new_rfid",
            },
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.attendee1.user.rfid, "new_rfid")

    def test_tries_to_save_rfid_with_unknown_username(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {
                "event": self.event.id,
                "username": self.attendee1.user.username + "fake",
                "rfid": "new_rfid",
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.USERNAME_DOES_NOT_EXIST,
        )

    def test_user_is_on_waitlist_username(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "username": self.attendee2.user.username},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.ON_WAIT_LIST,
        )

    def test_user_is_on_waitlist_rfid(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": self.attendee2.user.rfid},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.ON_WAIT_LIST,
        )

    def test_user_is_on_waitlist_approved(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {
                "event": self.event.id,
                "rfid": self.attendee2.user.rfid,
                "approved": True,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.REGISTER_SUCCESS,
        )

    def test_api_does_not_try_to_get_user_by_rfid_empty_string(self):
        self.event.attendance_event.max_capacity = 2
        self.event.attendance_event.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": ""},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertFalse(self.attendees[1].attended)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.USERNAME_AND_RFID_MISSING,
        )

    def test_save_rfid_give_no_username_gives_useful_error_message(self):
        self.attendee1.user.rfid = None
        self.attendee1.user.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": self.attendee1.user.rfid},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.USERNAME_AND_RFID_MISSING,
        )

    def test_save_rfid_gives_useful_error_message_if_rfid_already_exists(self):
        rfid = generate_valid_rfid()
        self.attendee1.user.rfid = None
        self.attendee1.user.save()
        self.attendee2.user.rfid = rfid
        self.attendee2.user.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {
                "event": self.event.id,
                "username": self.attendee1.user.username,
                "rfid": rfid,
            },
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.REGISTER_ERROR,
        )

    def test_wrong_committee_registering_attendance(self):
        wrong_committee = G(Group, name="Bedkom")
        self.committee.user_set.remove(self.user)
        self.committee.save()
        self.user.groups.add(wrong_committee)
        self.user.save()

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "username": self.attendee1.user.username},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_authenticated_user_registering_attendance(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "username": self.attendee1.user.username},
            **self.bare_headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rfid_for_non_attending_user_returns_useful_information(self):
        non_attending_user: OnlineUser = G(
            OnlineUser, username="non_attending", rfid="1010101010"
        )

        response = self.client.post(
            self.get_register_attendance_url(),
            {"event": self.event.id, "rfid": non_attending_user.rfid},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.USER_NOT_ATTENDING,
        )

    def test_attend_without_event_returns_correct_status(self):
        response = self.client.post(
            self.get_register_attendance_url(),
            {"username": self.attendee1.user.username},
            **self.headers,
        )

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("detail").get("attend_status"),
            AttendStatus.EVENT_ID_MISSING,
        )
