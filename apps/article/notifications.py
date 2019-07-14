from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage
from apps.notifications.handler import AbstractNotificationHandler
from apps.notifications.types import NotificationType

from .models import Article


class ArticleCreatedNotification(AbstractNotificationHandler):
    message_type = NotificationType.ARTICLE_CREATED
    recipients = User.objects.all()

    def __init__(self, article: Article, *args, **kwargs):
        self.article = article
        super().__init__(*args, **kwargs)

    def get_tag(self, user) -> str:
        return f'{self.get_type()}-{self.article.id}'

    def get_title(self, user) -> str:
        return f'Ny artikkel på fra Online, {self.article.heading}'

    def get_body(self, user) -> str:
        return self.article.ingress_short

    def get_url(self, user) -> str:
        return self.article.get_absolute_url()

    def get_image(self, user) -> ResponsiveImage:
        return self.article.image
