import logging

from django.db import models
from django.utils import timezone

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage

from .tasks import send_webpush
from .types import NotificationType

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

    def __str__(self):
        return f'{self.user} - {self.endpoint}'

    class Meta:
        verbose_name = 'Pushvarslingsabbonement'
        verbose_name_plural = 'Pushvarslingsabbonement'
        ordering = ('user', 'endpoint',)
        unique_together = (('user', 'endpoint'),)
        permissions = (
            ('view_notificationsubscription', 'View Notification Subscription'),
        )
        default_permissions = ('add', 'change', 'delete')


class NotificationSetting(models.Model):
    user = models.ForeignKey(to=User, related_name='notification_settings', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=100, choices=NotificationType.ALL_CHOICES)

    """ Different notification dispatchers """
    mail = models.BooleanField(default=False)
    push = models.BooleanField(default=False)

    @classmethod
    def get_for_user_by_type(cls, user: User, message_type: str) -> 'NotificationSetting':

        if message_type not in NotificationType.ALL_TYPES:
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
        missing_types = set(NotificationType.ALL_TYPES) - current_types
        logger.warning(missing_types)

        for message_type in missing_types:
            NotificationSetting.objects.create(user=user, message_type=message_type)

    def __str__(self):
        return f'{self.user} - {self.get_message_type_display()}'

    class Meta:
        verbose_name = 'Varselinnstilling'
        verbose_name_plural = 'Varselinnstillinger'
        ordering = ('user', 'message_type',)
        unique_together = (('user', 'message_type'),)
        permissions = (
            ('view_notificationsetting', 'View Notification Setting'),
        )
        default_permissions = ('add', 'change', 'delete')


def get_current_timestamp():
    return timezone.now().timestamp()


class Notification(models.Model):
    """
    Standard notification message which is sent to a single user on creation
    """
    """ Small badge used as the app-icon """
    badge = 'https://beta.online.ntnu.no/static/owf-badge-128.png'
    """ The vibration rythm, could be replaced with a more custom Online version """
    vibrate = [500, 110, 500, 110, 450, 110, 200, 110, 170, 40, 450, 110, 200, 110, 170, 40, 500]
    """ Tune played when the notification is triggered """
    sound = ''

    user = models.ForeignKey(
        to=User,
        related_name='notifications',
        on_delete=models.CASCADE,
        null=False, blank=False,
    )
    message_type = models.CharField(max_length=100, choices=NotificationType.ALL_CHOICES)
    sent = models.BooleanField(default=False)

    image = models.ForeignKey(
        to=ResponsiveImage,
        related_name='notifications',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    icon = models.URLField(default='https://beta.online.ntnu.no/static/pwa-icon-v0-192.png')
    title = models.CharField(max_length=60, null=False, blank=False)
    body = models.CharField(max_length=512, null=False, blank=False)
    tag = models.CharField(max_length=50, null=True, blank=True)

    require_interaction = models.BooleanField(default=False,)
    renotify = models.BooleanField(default=False,)
    silent = models.BooleanField(default=False,)
    timestamp = models.IntegerField(default=get_current_timestamp)
    url = models.URLField(default='/')

    @property
    def data(self):
        return {
            'badge': self.badge,
            'vibrate': self.vibrate,
            'sound': self.sound,
            'image': self.image.md,
            'icon': self.icon,
            'title': self.title,
            'body': self.body,
            'tag': self.tag,
            'require_interaction': self.require_interaction,
            'renotify': self.renotify,
            'silent': self.silent,
            'timestamp': self.timestamp,
            'url': self.url,
        }

    def dispatch(self):
        """
        Dispatch the notification to all subscribed units the user has.
        """
        """ Notifications should not be dispatched again if they have already been dispatched """
        if self.sent:
            return

        """ Message should not be sent if the user has disabled this type of notification """
        setting = NotificationSetting.get_for_user_by_type(self.user, self.message_type)
        if not setting.push:
            return

        subscriptions = NotificationSubscription.objects.filter(user=self.user)
        for subscription in subscriptions:
            send_webpush.delay(subscription=subscription, notification=self)

    def __str__(self):
        return f'{self.title} - {self.user}'

    class Meta:
        verbose_name = 'Varsel'
        verbose_name_plural = 'Varsler'
        ordering = ('timestamp', 'user', 'title',)
        permissions = (
            ('view_notification', 'View Notification'),
        )
        default_permissions = ('add', 'change', 'delete')
