from rest_framework import serializers

from apps.notifications.models import (
    Notification,
    Permission,
    Subscription,
    UserPermission,
)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "endpoint", "auth", "p256dh", "user")
        read_only_fields = ("user",)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "created_date",
            "sent_email",
            "sent_push",
            "title",
            "body",
            "url",
            "tag",
            "require_interaction",
            "renotify",
            "silent",
        )


class PermissionSerializer(serializers.ModelSerializer):
    permission_type_display = serializers.CharField(
        source="get_permission_type_display"
    )

    class Meta:
        model = Permission
        fields = (
            "id",
            "permission_type",
            "permission_type_display",
            "allow_email",
            "allow_push",
            "force_email",
            "force_push",
            "default_value_email",
            "default_value_push",
        )


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = (
            "id",
            "permission",
            "user",
            "allow_email",
            "allow_push",
        )
        read_only_fields = ("user", "permission")
