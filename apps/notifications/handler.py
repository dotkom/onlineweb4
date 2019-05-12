from django.db import models

from apps.authentication.models import OnlineUser as User
from apps.notifications.dispatcher import NotificationDispatcher


class AbstractNotificationHandler:
    """ Small notification badge. Used for things like notification icon in the top bar for Android """
    badge_url = ''
    """ Identifying icon for the notification """
    icon_url = ''
    """ Vibration pattern for the notification """
    vibrate: [int] = []

    @staticmethod
    def signal(sender, instance, **kwargs):
        raise NotImplementedError('NotificationHandler has to implement static method signal')

    def gather_recipients(self) -> models.QuerySet[User]:
        raise NotImplementedError('NotificationHandler has to implement gather_recipients')

    def resolve_settings(self) -> models.QuerySet[User]:
        raise NotImplementedError('NotificationHandler has to implement resolve_settings')

    def get_model_instance(self):
        raise NotImplementedError('NotificationHandler has to implement get_model_instance')

    def get_message_title(self, user: User, model_instance) -> str:
        """
        The main title of the notification
        """
        raise NotImplementedError('NotificationHandler has to implement get_message_title')

    def get_message_body(self, user: User, model_instance) -> str:
        """
        Main body/content of the notification. Will be hidden or only partly shown before the user
        interacts with the notification.
        """
        raise NotImplementedError('NotificationHandler has to implement get_message_body')

    def get_message_image_url(self, user: User, model_instance) -> str:
        """
        Optional image url for the notification.
        Displayed as a large image together with the body.
        """
        raise NotImplementedError('NotificationHandler has to implement get_message_image_url')

    def get_message_tag(self, user: User, model_instance) -> str:
        """
        Tag for notification. Identifies the notification.
        If the user receives a new notification with the same tag while another notification with the same tag
        is visible, the new one will replace it.
        """
        return f'{self.Meta.tag}-{self.get_model_instance().id}'

    def get_message_url(self, user: User, model_instance):
        return None

    def get_message_timestamp(self, user: User, model_instance) -> int:
        """
        Timestamp for notification as a unix timestamp.
        Displayed on the notification as when it was received.
        """
        return timezone.now().timestamp()

    def build_notification(self, user: User, model_instance):
        return {
            'title': self.get_message_title(user, model_instance),
            'body': self.get_message_body(user, model_instance),
            'image': self.get_message_image_url(user, model_instance),
            'tag': self.get_message_tag(user, model_instance),
            'timestamp': self.get_message_timestamp(user, model_instance),
            'icon': self.icon_url,
            'badge': self.badge_url,
            'vibrate': self.vibrate,
        }

    def dispatch(self, model_instance):
        users = self.gather_recipients()
        permitted_users = self.resolve_permissions(users)

        for user in permitted_users:
            notification = self.build_notification(user, model_instance)
            for dispatcher in self.Meta.dispatchers:
                dispatcher.dispatch(user, notification)

    class Meta:
        abstract = True
        dispatchers: list[NotificationDispatcher] = []
        tag = ''
