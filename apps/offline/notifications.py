from apps.authentication.models import OnlineUser as User
from apps.notifications.handler import AbstractNotificationHandler
from apps.notifications.types import NotificationType

from .models import Issue


class OfflineCreatedNotification(AbstractNotificationHandler):
    message_type = NotificationType.OFFLINE_CREATED
    recipients = User.objects.all()

    def __init__(self, issue: Issue, *args, **kwargs):
        self.issue = issue
        super().__init__(*args, **kwargs)

    def get_tag(self, user) -> str:
        return f'{self.get_type()}-{self.issue.id}'

    def get_title(self, user) -> str:
        return f'En ny versjon a Offline har blitt lastet opp'

    def get_body(self, user) -> str:
        return (f'{self.issue.title}\n'
                f'{self.issue.description}')

    def get_url(self, user) -> str:
        return self.issue.issue.url
