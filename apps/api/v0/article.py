#-*- coding: utf-8 -*-
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource

from apps.article.models import Article
from apps.api.v0.userprofile import UserResource

class ArticleResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by')

    class Meta:
        queryset = Article.objects.all()
        resource_name = 'article/all'
        
        ordering = ['published_date']
        filtering = {
            'published_date' : ('gte',)
        }
