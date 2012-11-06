#-*- coding: utf-8 -*-

from tastypie.resources import ModelResource
from apps.article.models import Article

class ArticleResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
