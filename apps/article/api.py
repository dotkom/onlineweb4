#-*- coding: utf-8 -*-
from apps.article.models import Article
from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from copy import copy
from tastypie import fields


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'article/user'
        # List of fields we do NOT want to make available
        excludes = ['password',
                    'email',
                    'date_joined'
                    'id',
                    'last_login']

class ArticleResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by', full=True)
    class Meta:
        queryset = Article.objects.all()
        resource_name = 'article/all'
