from django.apps import AppConfig


class ArticleConfig(AppConfig):
    name = "apps.article"
    verbose_name = "Article"

    def ready(self):
        super(ArticleConfig, self).ready()

        from watson import search as watson

        from apps.article.models import Article

        watson.register(Article)
