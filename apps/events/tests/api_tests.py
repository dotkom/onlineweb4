from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from oauth2_provider.models import (get_access_token_model, get_application_model, get_grant_model,
                                    get_refresh_token_model)
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser

from .utils import attend_user_to_event, generate_event

Application = get_application_model()
Grant = get_grant_model()
AccessToken = get_access_token_model()
RefreshToken = get_refresh_token_model()


def generate_attendee(event, username, rfid):
    user = G(OnlineUser, username=username, rfid=rfid)
    return attend_user_to_event(event, user)


class EventsAPIURLTestCase(APITestCase):
    def test_events_list_empty(self):
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_list_exists(self):
        generate_event()
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):
        event = generate_event()
        url = reverse('events-detail', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AttendAPITestCase(APITestCase):
    def setUp(self):
        self.user = G(OnlineUser, name='test_user')
        self.application = Application.objects.create(
            name='test_client', user=self.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            scopes='read write regme.readwrite',
            redirect_uris='http://localhost',
        )
        self.application.save()
        self.access_token = AccessToken.objects.create(
            user=self.user, token='1234567890',
            application=self.application, scope='read write regme.readwrite',
            expires=timezone.now() + timedelta(days=1)
        )
        self.access_token.save()
        self.headers = {
            'format': 'json',
            'HTTP_AUTHORIZATION': 'Bearer ' + self.access_token.token,
        }
        self.url = reverse('event_attend')
        self.event = generate_event()
        self.attendee1 = generate_attendee(self.event, 'test1', '123')
        self.attendee2 = generate_attendee(self.event, 'test2', '321')
        self.attendees = [self.attendee1, self.attendee2]

    def refresh_attendees(self):
        for attendee in self.attendees:
            attendee.refresh_from_db()
            attendee.user.refresh_from_db()

    def test_missing_auth_returns_unauthorized(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_scope_returns_forbidden(self):
        self.access_token.scope = 'read write wrongme.readwrite'
        self.access_token.save()

        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(response.json()['attend_status'], 10)

    def test_attend_with_rfid(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee1.user.rfid,
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.attendee1.attended)
        self.assertFalse(self.attendee2.attended)
        self.assertEqual(response.json()['attend_status'], 10)

    def test_attend_twice(self):
        self.attendee1.attended = True
        self.attendee1.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee1.user.rfid,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['attend_status'], 20)

    def test_unknown_rfid(self):
        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': 'fake_rfid',
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['attend_status'], 40)

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
        self.assertEqual(response.json()['attend_status'], 50)

    def test_user_is_on_waitlist_username(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'username': self.attendee2.user.username,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['attend_status'], 30)

    def test_user_is_on_waitlist_rfid(self):
        self.event.attendance_event.max_capacity = 1
        self.event.attendance_event.waitlist = True
        self.event.attendance_event.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': self.attendee2.user.rfid,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['attend_status'], 30)

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
        self.assertEqual(response.json()['attend_status'], 10)

    def test_api_does_not_try_to_get_user_by_rfid_empty_string(self):
        self.event.attendance_event.max_capacity = 2
        self.event.attendance_event.save()

        self.attendee1.user.rfid = ''
        self.attendee2.user.rfid = ''
        self.attendee1.user.save()
        self.attendee2.user.save()

        response = self.client.post(self.url, {
            'event': self.event.id,
            'rfid': '',
        }, **self.headers)

        self.refresh_attendees()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.attendees[0].attended)
        self.assertFalse(self.attendees[1].attended)
        self.assertEqual(response.json()['attend_status'], 41)
