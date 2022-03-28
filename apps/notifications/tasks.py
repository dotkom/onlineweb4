import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from pywebpush import WebPushException, webpush
from rest_framework import serializers

try:
    from zappa.asynchronous import task
except ImportError:
    # Zappa is only required if we are running on Lambda
    def task(func):
        return func


from .constants import (
    NOTIFICATION_BADGE_URL,
    NOTIFICATION_ICON_URL,
    NOTIFICATION_SOUND,
    NOTIFICATION_VIBRATION_PATTERN,
)
from .models import Notification

logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = settings.WEB_PUSH_PRIVATE_KEY
WEB_PUSH_ENABLED = settings.WEB_PUSH_ENABLED

VAPID_CLAIMS = {
    "sub": "mailto:dotkom@online.ntnu.no",
}


def _send_webpush(subscription_info: dict, data: dict) -> bool:
    """
    Send a webpush message asynchronously
    """
    if not WEB_PUSH_ENABLED:
        return False

    json_data = json.dumps(data)

    try:
        webpush(
            subscription_info=subscription_info,
            data=json_data,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
        return True
    except WebPushException as error:
        logger.error(error)
        # Mozilla returns additional information in the body of the response.
        if error.response and error.response.json():
            logger.error(error.response.json())
        return False
    except TypeError as error:
        logger.error(error)
        raise error


class NotificationDataSerializer(serializers.ModelSerializer):
    """
    Transform a Notification object to a valid notification message as
    defined by the web push notification spec.
    https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification
    Note that the object is flattened, as in 'title' and 'options' are in the same object.
    These need to be separated on the client.
    """

    badge = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    vibrate = serializers.SerializerMethodField()
    sound = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_badge(self, obj: Notification):
        return NOTIFICATION_BADGE_URL

    def get_icon(self, obj: Notification):
        return NOTIFICATION_ICON_URL

    def get_vibrate(self, obj: Notification):
        return NOTIFICATION_VIBRATION_PATTERN

    def get_sound(self, obj: Notification):
        return NOTIFICATION_SOUND

    def get_timestamp(self, obj: Notification):
        return obj.created_date.timestamp()

    def get_image(self, obj: Notification):
        if obj.image:
            return f"{settings.BASE_URL}{obj.image.md}"
        return None

    class Meta:
        model = Notification
        fields = (
            "badge",
            "vibrate",
            "sound",
            "image",
            "icon",
            "title",
            "body",
            "tag",
            "require_interaction",
            "renotify",
            "silent",
            "timestamp",
            "url",
        )


@task
def dispatch_push_notification_task(notification_id: int):
    notification = Notification.objects.get(pk=notification_id)
    user = notification.recipient
    notification_data = NotificationDataSerializer(notification).data

    results = []
    for subscription in user.notification_subscriptions.all():
        subscription_info = subscription.to_vapid_format()
        result = _send_webpush(subscription_info, data=notification_data)
        results.append(result)

    did_any_message_succeed = any(results)
    notification.sent_push = did_any_message_succeed
    notification.save()


@task
def dispatch_email_notification_task(notification_id: int):
    notification = Notification.objects.get(pk=notification_id)
    user = notification.recipient

    send_mail(
        subject=notification.title,
        message=notification.body,
        from_email=notification.from_email,
        recipient_list=[user.primary_email],
        fail_silently=False,
    )

    notification.sent_email = True
    notification.save()
