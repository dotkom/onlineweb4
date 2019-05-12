from rest_framework import serializers

from apps.notifications.models import NotificationSetting, NotificationSubscription


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

    class Meta:
        model = NotificationSetting
        fields = (
            'id', 'message_type', 'mail', 'push', 'user',
        )
        read_only_fields = ('message_type', 'user', 'id')
