from django.apps import AppConfig

import watson


class ArticleConfig(AppConfig):
    name = 'apps.article'
    verbose_name = 'Article'

    def ready(self):
        super(ArticleConfig, self).ready()

        from apps.article.models import Article

        watson.register(Article)
