import json

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from onlineweb4.fields.recaptcha import mock_validate_recaptcha
from rest_framework import status

from apps.authentication.models import OnlineUser
from apps.companyprofile.models import Company
from apps.events.constants import AttendStatus
from apps.events.models import Attendee, CompanyEvent
from apps.online_oidc_provider.test import OIDCTestCase
from apps.profiles.models import Privacy

from .utils import (attend_user_to_event, generate_event, generate_payment, generate_user,
                    pay_for_event)


def generate_attendee(event, username, rfid):
    user = G(OnlineUser, username=username, rfid=rfid)
    return attend_user_to_event(event, user)


def generate_valid_rfid():
    return '12345678'


class CreateAttendeeTestCase(OIDCTestCase):

    def setUp(self):

        self.committee = G(Group, name='arrKom')
        self.user = generate_user(username='_user')
        self.privacy = G(Privacy, user=self.user)
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
        }
        self.recaptcha_arg = {'recaptcha': '--mock-recaptcha--'}

        self.url = reverse('registration_attendees-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.event = generate_event(organizer=self.committee)
        self.event.attendance_event.registration_start = timezone.now()
        self.event.attendance_event.registration_end = timezone.now() + timezone.timedelta(days=2)
        self.event.attendance_event.max_capacity = 20
        self.event.attendance_event.save()
        self.attendee1 = generate_attendee(self.event, 'test1', '4321')
        self.attendee2 = generate_attendee(self.event, 'test2', '1234')
        self.attendees = [self.attendee1, self.attendee2]

    @mock_validate_recaptcha()
    def test_user_cannot_attend_a_non_attendance_event(self, _):
        event_without_attendance = generate_event(organizer=self.committee, attendance=False)

        response = self.client.post(self.url, {
            'event': event_without_attendance.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.json(), ['Dette er ikke et påmeldingsarrangement'])

    @mock_validate_recaptcha()
    def test_guest_user_can_attend_event_with_guest_attendance(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(attendance.is_attendee(self.user))

    @mock_validate_recaptcha()
    def test_guest_user_cannot_attend_other_users_to_events(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        other_user = generate_user(username='other_user')

        response = self.client.post(self.url, {
            'event': self.event.id,
            'user': other_user.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(attendance.is_attendee(other_user))
        self.assertEqual(response.json().get('user'), ['Du kan ikke melde andre brukere på arrangementer!'])

    @mock_validate_recaptcha()
    def test_show_as_attending_event_is_set_false_by_default(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.json().get('show_as_attending_event'))

    @mock_validate_recaptcha()
    def test_user_can_set_show_as_attending_event_on_registration(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        self.privacy.visible_as_attending_events = True
        self.privacy.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'show_as_attending_event': True,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json().get('show_as_attending_event'))

    @mock_validate_recaptcha()
    def test_user_can_change_show_as_attending_event_after_registering(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        self.privacy.visible_as_attending_events = False
        self.privacy.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        attendee_id = response.json().get('id')
        attendance.registration_end = timezone.now() + timezone.timedelta(hours=1)
        attendance.unattend_deadline = timezone.now() + timezone.timedelta(hours=1)
        attendance.save()

        patch_response = self.client.patch(self.id_url(attendee_id), {
            'show_as_attending_event': True,
        }, **self.headers)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.json().get('show_as_attending_event'), True)

    @mock_validate_recaptcha()
    def test_user_can_change_show_as_attending_event_if_registration_has_ended(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        self.privacy.visible_as_attending_events = False
        self.privacy.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        attendee_id = response.json().get('id')
        attendance.registration_end = timezone.now() - timezone.timedelta(hours=1)
        attendance.save()

        patch_response = self.client.patch(self.id_url(attendee_id), {
            'show_as_attending_event': True,
        }, **self.headers)

        attendee = Attendee.objects.get(pk=attendee_id)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(attendee.show_as_attending_event, True)

    def test_guest_user_cannot_attend_event_with_guest_attendance_without_captcha(self):
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(attendance.is_attendee(self.user))
        self.assertEqual(response.json().get('recaptcha'), ['Dette feltet er påkrevd.'])

    @mock_validate_recaptcha()
    def test_user_cannot_attend_twice(self, _):
        attendance = self.event.attendance_event
        initial_attendees = len(attendance.attendees.all())

        self.test_guest_user_can_attend_event_with_guest_attendance()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors'), ['Feltene event, user må gjøre et unikt sett.'])
        self.assertEqual(len(attendance.attendees.all()), initial_attendees + 1)

    @mock_validate_recaptcha()
    def test_guest_user_cannot_attend_event_without_guest_attendance(self, _):
        attendance = self.event.attendance_event
        attendance.guest_attendance = False
        attendance.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors'), ['Dette arrangementet er kun åpent for medlemmer.'])

    @mock_validate_recaptcha()
    def test_user_cannot_attend_event_after_registration_end(self, _):
        attendance = self.event.attendance_event
        attendance.registration_start = timezone.now() - timezone.timedelta(days=2)
        attendance.registration_end = timezone.now() - timezone.timedelta(days=2)
        attendance.guest_attendance = True
        attendance.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors'), ['Påmeldingen er ikke lenger åpen.'])

    def test_user_can_unattend_before_deadline(self):
        self.event.attendance_event.unattend_deadline = timezone.now() + timezone.timedelta(days=2)
        self.event.event_start = timezone.now() + timezone.timedelta(days=3)
        self.event.attendance_event.save()
        self.event.save()
        attendee = attend_user_to_event(self.event, self.user)

        response = self.client.delete(self.id_url(attendee.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.event.attendance_event.is_attendee(self.user))

    def test_user_cannot_unattend_after_deadline_has_passed(self):
        self.event.attendance_event.unattend_deadline = timezone.now() - timezone.timedelta(days=2)
        self.event.attendance_event.save()
        attendee = attend_user_to_event(self.event, self.user)

        response = self.client.delete(self.id_url(attendee.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.event.attendance_event.is_attendee(self.user))
        self.assertEqual(
            response.json().get('message'),
            'Avmeldingsfristen har gått ut, det er ikke lenger mulig å melde seg av arrangementet.'
        )

    def test_user_cannot_unattend_after_event_has_started(self):
        self.event.attendance_event.unattend_deadline = timezone.now() + timezone.timedelta(days=2)
        self.event.event_start = timezone.now() - timezone.timedelta(hours=1)
        self.event.attendance_event.save()
        self.event.save()
        attendee = attend_user_to_event(self.event, self.user)

        response = self.client.delete(self.id_url(attendee.id), **self.headers)

        self.assertEqual(
            response.json().get('message'),
            'Du kan ikke melde deg av et arrangement som allerde har startet.'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.event.attendance_event.is_attendee(self.user))
        self.assertEqual(
            response.json().get('message'),
            'Du kan ikke melde deg av et arrangement som allerde har startet.'
        )

    def test_user_can_re_attend_and_event_after_un_attending(self):
        self.test_user_can_unattend_before_deadline()
        self.test_guest_user_can_attend_event_with_guest_attendance()

    @mock_validate_recaptcha()
    def test_payment_is_generated_on_attendance(self, _):
        generate_payment(self.event)
        attendance = self.event.attendance_event
        attendance.guest_attendance = True
        attendance.save()

        attend_response = self.client.post(self.url, {
            'event': self.event.id,
            **self.recaptcha_arg,
        }, **self.headers)

        self.assertEqual(attend_response.status_code, status.HTTP_201_CREATED)

        pay_for_event(self.event, self.user)
        attendee_id = attend_response.json()['id']

        attendee_response = self.client.get(self.id_url(attendee_id), {
            'event': self.event.id,
        }, **self.headers)

        self.assertEqual(attendee_response.status_code, status.HTTP_200_OK)
        self.assertTrue(attendee_response.json()['has_paid'])


class EventsAPITestCase(OIDCTestCase):

    def setUp(self):

        self.committee = G(Group, name='bedKom')
        self.user = generate_user(username='_user')
        self.privacy = G(Privacy, user=self.user)
        self.token = self.generate_access_token(self.user)

        self.url = reverse('events-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.event = generate_event(organizer=self.committee)
        self.event.attendance_event.registration_start = timezone.now()
        self.event.attendance_event.registration_end = timezone.now() + timezone.timedelta(days=2)
        self.event.attendance_event.max_capacity = 20
        self.event.attendance_event.save()
        self.attendee1 = generate_attendee(self.event, 'test1', '1231')
        self.attendee2 = generate_attendee(self.event, 'test2', '4321')
        self.attendees = [self.attendee1, self.attendee2]

    def test_events_list_empty(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):

        response = self.client.get(self.id_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_list_exists(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        events_list = response.json().get('results')
        event_titles_list = list(map(lambda event: event.get('title'), events_list))

        self.assertIn(self.event.title, event_titles_list)

    def test_filter_companies_in_event_list(self):
        onlinecorp: Company = G(Company, name='onlinecorp')
        bedpres_with_onlinecorp = generate_event(organizer=self.committee)
        G(CompanyEvent, company=onlinecorp, event=bedpres_with_onlinecorp)
        evilcorp: Company = G(Company, name='evilcorp')
        bedpres_with_evilcorp = generate_event(organizer=self.committee)
        G(CompanyEvent, company=evilcorp, event=bedpres_with_evilcorp)

        response = self.client.get(f'{self.url}?companies={onlinecorp.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        events_list = response.json().get('results')
        event_titles_list = list(map(lambda event: event.get('id'), events_list))

        self.assertIn(bedpres_with_onlinecorp.id, event_titles_list)
        self.assertNotIn(bedpres_with_evilcorp.id, event_titles_list)


class AttendAPITestCase(OIDCTestCase):

    def setUp(self):
        self.committee = G(Group, name='arrKom')
        self.user = G(OnlineUser, name='test_user', groups=[self.committee])
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'format': 'json',
        }

        self.url = reverse('attendees-register-attendance')
        self.event = generate_event(organizer=self.committee)
        self.attendee1 = generate_attendee(self.event, 'test1', '0123')
        self.attendee2 = generate_attendee(self.event, 'test2', '3210')
        self.attendees = [self.attendee1, self.attendee2]

    def refresh_attendees(self):
        for attendee in self.attendees:
            attendee.refresh_from_db()
            attendee.user.refresh_from_db()

    def test_missing_auth_returns_unauthorized(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_data_returns_bad_request(self):
        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attend_with_username(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee1.user.username,
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.attendee1.attended)
        self.assertFalse(self.attendee2.attended)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.REGISTER_SUCCESS)

    def test_attend_with_rfid(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee1.user.rfid,
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.attendee1.attended)
        self.assertFalse(self.attendee2.attended)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.REGISTER_SUCCESS)

    def test_attend_twice(self):
        self.attendee1.attended = True
        self.attendee1.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee1.user.rfid,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.PREVIOUSLY_REGISTERED)

    def test_unknown_rfid(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': 'fake_rfid',
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.RFID_DOES_NOT_EXIST)

    def test_saves_rfid(self):

        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee1.user.username,
            'rfid': 'new_rfid',
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.attendee1.user.rfid, 'new_rfid')

    def test_tries_to_save_rfid_with_unknown_username(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee1.user.username + 'fake',
            'rfid': 'new_rfid',
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.USERNAME_DOES_NOT_EXIST)

    def test_user_is_on_waitlist_username(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee2.user.username,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.ON_WAIT_LIST)

    def test_user_is_on_waitlist_rfid(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee2.user.rfid,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.ON_WAIT_LIST)

    def test_user_is_on_waitlist_approved(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee2.user.rfid,
            'approved': True
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.REGISTER_SUCCESS)

    def test_api_does_not_try_to_get_user_by_rfid_empty_string(self):
        self.event.attendance_event.max_capacity = 2
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': '',
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertFalse(self.attendees[1].attended)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.USERNAME_AND_RFID_MISSING)

    def test_save_rfid_give_no_username_gives_useful_error_message(self):
        self.attendee1.user.rfid = None
        self.attendee1.user.save()

        response = self.client.post(self.url, json.dumps({
            'event': self.event.id,
            'rfid': self.attendee1.user.rfid,
        }), content_type='application/json', **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.USERNAME_AND_RFID_MISSING)

    def test_save_rfid_gives_useful_error_message_if_rfid_already_exists(self):
        rfid = generate_valid_rfid()
        self.attendee1.user.rfid = None
        self.attendee1.user.save()
        self.attendee2.user.rfid = rfid
        self.attendee2.user.save()

        response = self.client.post(self.url, json.dumps({
            'event': self.event.id,
            'username': self.attendee1.user.username,
            'rfid': rfid,
        }), content_type='application/json', **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.REGISTER_ERROR)

    def test_wrong_committee_registering_attendance(self):
        wrong_committee = G(Group, name='bedKom')
        self.committee.user_set.remove(self.user)
        self.committee.save()
        self.user.groups.add(wrong_committee)
        self.user.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee1.user.username,
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_authenticated_user_registering_attendance(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee1.user.username,
        }, headers={'format': 'json'})

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rfid_for_non_attending_user_returns_useful_information(self):
        non_attending_user: OnlineUser = G(OnlineUser, username='non_attending', rfid='1010101010')

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': non_attending_user.rfid,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.USER_NOT_ATTENDING)

    def test_attend_without_event_returns_correct_status(self):
        response = self.client.post(self.url, {
            'username': self.attendee1.user.username,
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail').get('attend_status'), AttendStatus.EVENT_ID_MISSING)
