import logging

from django.utils import timezone
from django.db import models

from apps.authentication.models import OnlineUser as User

from .dispatcher import NotificationDispatcher

from .types import NOTIFICATION_TYPES

logger = logging.getLogger(__name__)


class NotificationSubscription(models.Model):
    """
    Model describing a webpush notification subscription.
    """
    user = models.ForeignKey(to=User, related_name='notification_subscriptions', on_delete=models.CASCADE)

    """ Identifiers and keys used to send the push notification. Can be really damned long """
    endpoint = models.URLField(unique=True, max_length=500)
    auth = models.CharField(unique=True, max_length=500)
    p256dh = models.CharField(unique=True, max_length=500)

    class Meta:
        verbose_name = 'Pushvarslingsabbonement'
        verbose_name_plural = 'Pushvarslingsabbonement'


NOTIFICATION_CHOICES = [(noti, noti) for noti in NOTIFICATION_TYPES]


class NotificationSetting(models.Model):
    user = models.ForeignKey(to=User, related_name='notification_settings', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=100, choices=NOTIFICATION_CHOICES)

    """ Different notification dispatchers """
    mail = models.BooleanField(default=False)
    push = models.BooleanField(default=False)

    @classmethod
    def get_for_user_by_type(cls, user: User, message_type: str):

        if message_type not in NOTIFICATION_TYPES:
            raise ValueError('Notification type does not exist')

        """ Make sure the notification setting exists for the user before getting it """
        cls.create_all_for_user(user)

        try:
            return cls.objects.get(user=user, message_type=message_type)
        except cls.DoesNotExist:
            logger.error(f'Notification setting: {message_type} does not exist for user: {user}')

    @classmethod
    def create_all_for_user(cls, user: User):
        """
        Create all missing notification types as settings for the user is they are missing.
        """
        current_types = set([setting.message_type for setting in cls.objects.filter(user=user)])
        logger.warning(current_types)
        missing_types = set(NOTIFICATION_TYPES) - current_types
        logger.warning(missing_types)

        for message_type in missing_types:
            NotificationSetting.objects.create(user=user, message_type=message_type)
