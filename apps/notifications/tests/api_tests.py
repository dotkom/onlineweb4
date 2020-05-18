from django_dynamic_fixture import G
from rest_framework import status

from apps.notifications.models import (
    Notification,
    Permission,
    Subscription,
    UserPermission,
)
from apps.online_oidc_provider.test import OIDCTestCase


class SubscriptionTestCase(OIDCTestCase):
    basename = "notifications_subscriptions"

    def setUp(self):
        self.subscription: Subscription = G(Subscription, user=self.user)

    def test_subscriptions_view_returns_200(self):
        response = self.client.get(self.get_list_url(), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_subscriptions(self):
        response = self.client.get(
            self.get_detail_url(self.subscription.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.subscription.id)

    def test_user_can_delete_their_own_subscriptions(self):
        response = self.client.delete(
            self.get_detail_url(self.subscription.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class NotificationTestCase(OIDCTestCase):
    basename = "notifications_messages"

    def setUp(self):
        self.subscription: Subscription = G(Subscription, user=self.user)
        self.notification: Notification = G(Notification, recipient=self.user)

    def test_notifications_view_returns_200(self):
        response = self.client.get(self.get_list_url(), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_notifications(self):
        response = self.client.get(
            self.get_detail_url(self.notification.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.notification.id)


class PermissionTestCase(OIDCTestCase):
    basename = "notifications_permissions"

    def setUp(self):
        self.permission: Permission = G(Permission)

    def test_notifications_view_returns_200(self):
        response = self.client.get(self.get_list_url(), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_permission_detail(self):
        response = self.client.get(
            self.get_detail_url(self.permission.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.permission.id)


class UserPermissionTestCase(OIDCTestCase):
    basename = "notifications_user_permissions"

    def setUp(self):
        self.permission: Permission = G(Permission)

    def test_subscriptions_view_returns_200(self):
        response = self.client.get(self.get_list_url(), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_403(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_their_own_permission(self):
        user_permission: UserPermission = G(
            UserPermission, user=self.user, permission=self.permission
        )
        response = self.client.get(
            self.get_detail_url(user_permission.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.permission.id)

    def test_user_can_create_user_permission(self):
        response = self.client.post(
            self.get_list_url(), {"permission": self.permission.id}, **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_delete_user_permission(self):
        user_permission: UserPermission = G(
            UserPermission, user=self.user, permission=self.permission
        )
        response = self.client.delete(
            self.get_detail_url(user_permission.id), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
