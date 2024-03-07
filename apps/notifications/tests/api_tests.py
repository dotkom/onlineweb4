from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser
from apps.notifications.models import (
    Notification,
    Permission,
    Subscription,
    UserPermission,
)
from onlineweb4.testing import GetUrlMixin

from .utils import NotificationTestMixin


class SubscriptionTestCase(GetUrlMixin, NotificationTestMixin, APITestCase):
    basename = "notifications_subscriptions"

    def setUp(self):
        self.user = G(OnlineUser)
        self.client.force_authenticate(user=self.user)
        self.subscription: Subscription = G(Subscription, user=self.user)

    def test_subscriptions_view_returns_200(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_own_subscriptions(self):
        response = self.client.get(self.get_detail_url(self.subscription.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.subscription.id)

    def test_user_can_delete_their_own_subscriptions(self):
        response = self.client.delete(self.get_detail_url(self.subscription.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_create_subscription(self):
        subscription = self._gen_subscription_info()
        subscription_data = {
            "endpoint": subscription.get("endpoint"),
            "auth": subscription.get("keys").get("auth").decode("utf-8"),
            "p256dh": subscription.get("keys").get("p256dh").decode("utf-8"),
        }

        response = self.client.post(self.get_list_url(), subscription_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class NotificationTestCase(GetUrlMixin, APITestCase):
    basename = "notifications_messages"

    def setUp(self):
        self.user = G(OnlineUser)
        self.client.force_authenticate(user=self.user)
        self.subscription: Subscription = G(Subscription, user=self.user)
        self.notification: Notification = G(Notification, recipient=self.user)

    def test_notifications_view_returns_200(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_own_notifications(self):
        response = self.client.get(self.get_detail_url(self.notification.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.notification.id)


class PermissionTestCase(GetUrlMixin, APITestCase):
    basename = "notifications_permissions"

    def setUp(self):
        self.user = G(OnlineUser)
        self.client.force_authenticate(user=self.user)
        self.permission: Permission = G(Permission)

    def test_notifications_view_returns_200(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_permission_detail(self):
        response = self.client.get(self.get_detail_url(self.permission.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.permission.id)


class UserPermissionTestCase(GetUrlMixin, APITestCase):
    basename = "notifications_user_permissions"

    def setUp(self):
        self.user = G(OnlineUser)
        self.client.force_authenticate(user=self.user)
        self.permission: Permission = G(Permission)

    def test_subscriptions_view_returns_200(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_own_permission(self):
        user_permission: UserPermission = G(
            UserPermission, user=self.user, permission=self.permission
        )
        response = self.client.get(self.get_detail_url(user_permission.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), user_permission.id)

    def test_user_can_update_user_permission(self):
        user_permission: UserPermission = G(
            UserPermission, user=self.user, permission=self.permission
        )
        new_value = not user_permission.allow_push
        response = self.client.patch(
            self.get_detail_url(user_permission.id),
            {"allow_push": new_value},
        )
        user_permission.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_permission.allow_push, new_value)
