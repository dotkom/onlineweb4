#-*- coding: utf-8 -*-

from tastypie.resources import ModelResource
from apps.article.mdoels import Article

class ArticleResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
