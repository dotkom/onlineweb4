from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.notifications.models import Notification, NotificationSetting, NotificationSubscription
from apps.notifications.types import NotificationType
from apps.oidc_provider.test import OIDCTestCase


class NotificationSettingsTestCase(OIDCTestCase):

    def setUp(self):
        self.user = G(User, username='_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
        }

        self.url = reverse('notifications_settings-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        NotificationSetting.create_all_for_user(self.user)

    def get_setting(self, setting: str) -> NotificationSetting:
        return NotificationSetting.get_for_user_by_type(self.user, setting)

    def test_settings_view_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_settings(self):
        setting = self.get_setting(NotificationType.EVENT_UPDATES)
        response = self.client.get(self.id_url(setting.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), setting.id)

    def test_user_can_update_settings(self):
        setting = self.get_setting(NotificationType.EVENT_UPDATES)
        setting.push = False
        setting.save()

        response = self.client.patch(self.id_url(setting.id), {
            'push': True,
        }, **self.headers)

        setting.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(setting.push)
        self.assertEqual(response.json().get('push'), setting.push)


class NotificationSubscriptionTestCase(OIDCTestCase):

    def setUp(self):
        self.user = G(User, username='_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
        }

        self.url = reverse('notifications_subscriptions-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        NotificationSetting.create_all_for_user(self.user)
        self.subscription: NotificationSubscription = G(NotificationSubscription, user=self.user)

    def test_subscriptions_view_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_subscriptions(self):
        response = self.client.get(self.id_url(self.subscription.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.subscription.id)


class NotificationTestCase(OIDCTestCase):

    def setUp(self):
        self.user = G(User, username='_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'content_type': 'application/json',
            'format': 'json',
        }

        self.url = reverse('notifications_messages-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'

        NotificationSetting.create_all_for_user(self.user)
        self.subscription: NotificationSubscription = G(NotificationSubscription, user=self.user)
        self.notification: Notification = G(Notification, user=self.user)

    def test_notifications_view_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_notifications(self):
        response = self.client.get(self.id_url(self.notification.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.notification.id)
