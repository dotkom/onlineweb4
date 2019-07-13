from rest_framework import serializers

from apps.notifications.models import Notification, NotificationSetting, NotificationSubscription


class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = NotificationSubscription
        fields = ('id', 'endpoint', 'auth', 'p256dh', 'user')


class NotificationSettingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    verbose_type = serializers.SerializerMethodField()

    def get_verbose_type(self, setting: NotificationSetting):
        return setting.get_message_type_display()

    class Meta:
        model = NotificationSetting
        fields = (
            'id', 'message_type', 'mail', 'push', 'user', 'verbose_type',
        )
        read_only_fields = ('message_type', 'user', 'id')


class NotificationReadOnlySerializer(serializers.ModelSerializer):
    verbose_type = serializers.SerializerMethodField()

    def get_verbose_type(self, setting: NotificationSetting):
        return setting.get_message_type_display()

    class Meta:
        model = Notification
        fields = (
            'id', 'message_type', 'sent', 'title', 'body', 'tag', 'badge', 'image', 'icon', 'require_interaction',
            'renotify', 'silent', 'timestamp', 'url', 'verbose_type',
        )
        read_only = True
