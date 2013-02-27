#-*- coding: utf-8 -*-
from copy import copy

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

class ArticleLatestResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by')
    
    class Meta:
        queryset = Article.objects.all()
        
        resource_name = 'article/latest'
        filtering = {
            'featured': ('exact',)
        }
        ordering = ['published_date',]
        max_limit = 25
    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'articles'.
        if isinstance(data, dict):
            data['articles'] = copy(data['objects'])
            del(data['objects'])
        return data
