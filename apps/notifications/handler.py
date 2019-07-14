import logging

from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage

from .models import Notification, NotificationSetting

logger = logging.getLogger(__name__)


class AbstractNotificationHandler:
    message_type: str = None
    notifications: [Notification] = []
    recipients: [User] = []

    title: str = None
    body: str = None
    require_interaction: bool = None
    renotify: bool = None
    silent: bool = None
    url: str = None
    icon: str = None
    tag: str = None

    def get_type(self):
        return self.message_type

    def get_title(self, user: User) -> str:
        """
        The main title of the notification
        """
        if self.title is None:
            raise NotImplementedError('NotificationHandler has to implement get_title')
        return self.title

    def get_body(self, user: User) -> str:
        """
        Main body/content of the notification. Will be hidden or only partly shown before the user
        interacts with the notification.
        """
        return self.body

    def get_image(self, user: User) -> ResponsiveImage:
        """
        Optional image url for the notification.
        Displayed as a large image together with the body.
        """
        return None

    def get_tag(self, user: User) -> str:
        """
        Tag for notification. Identifies the notification.
        If the user receives a new notification with the same tag while another notification with the same tag
        is visible, the new one will replace it.
        """
        return self.tag

    def get_url(self, user: User) -> str:
        """
        The URL the user will be directed tot when clicking the notification.
        """
        return self.url

    def get_icon(self, user: User) -> str:
        """
        The icon displayed beside the notification title/body.
        """
        return self.icon

    def __init__(self, recipients=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if recipients is not None:
            self.recipients = recipients
        self.create_notification()

    def get_recipients(self):
        return self.recipients

    def create_notification(self):
        settings = NotificationSetting.objects.filter(
            message_type=self.get_type(),
            user__in=self.get_recipients(),
        )
        users = [setting.user for setting in settings if setting.push or setting.mail]

        for user in users:
            data = {
                'title': self.get_title(user),
                'body': self.get_body(user),
                'image': self.get_image(user),
                'tag': self.get_tag(user),
                'url': self.get_url(user),
                'icon': self.get_icon(user),
                'message_type': self.get_type(),
                'user': user.id,
            }
            non_null_data = {key: value for key, value in data.items() if value is not None}

            notification_serializer = NotificationCreateSerializer(data=non_null_data)

            try:
                notification_serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as error:
                logger.error(f'Failed at creating notification for user: {user}', error)

            notification = notification_serializer.save()
            self.notifications.append(notification)

    def dispatch(self):
        for notification in self.notifications:
            notification.dispatch()

    class Meta:
        abstract = True


class NotificationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
