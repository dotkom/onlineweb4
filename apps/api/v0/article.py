#-*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from django.conf import settings

from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource

from apps.article.models import Article, ArticleTag, Tag
from apps.api.v0.userprofile import UserResource

from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS

class ArticleResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by')
    
    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'articles'.
        if isinstance(data, dict):
            data['articles'] = copy(data['objects'])
            del(data['objects'])
        return data
    
    # Making multiple images for the article
    def dehydrate(self, bundle):
        
        # If image is set
        if bundle.data['image']:
            # Parse to FileObject used by Filebrowser
            temp_image = FileObject(bundle.data['image'])
            
            # Itterate the different versions (by key)
            for ver in VERSIONS.keys():
                # Check if the key start with article_ (if it does, we want to crop to that size)
                if ver.startswith('article_'):
                    # Adding the new image to the object
                    bundle.data['image_'+ver] = temp_image.version_generate(ver).url
            
            # Unset the image-field
            del(bundle.data['image'])
            
            # Returning washed object
        return bundle
    
    def get_object_list(self, request):
        # Ugly hack to get the get-params (if they are set)
        try:
            request_tag = request.GET['tag']
        except:
            request_tag = None
        
        try:
            request_year = request.GET['year']
        except:
            request_year = None
        
        try:
            request_month = request.GET['month']
        except:
            request_month = None
        
        # Check filtering here
        if (request_year is not None):
            if (request_month is not None):
                # Filtering on both year and month
                queryset = Article.objects.filter(published_date__year=request_year, published_date__month=request_month)
            else:
                # Filtering on only year
                queryset = Article.objects.filter(published_date__year=request_year)
        else:
            # Not filtering on year, check if filtering on slug (tag) or return default query
            if (request_tag is not None):
                # Filtering on slug
                slug_query = Tag.objects.filter(slug = request_tag)
                slug_connect = ArticleTag.objects.filter(tag = slug_query).values('article_id')
                queryset = Article.objects.filter(id__in = slug_connect)
                #queryset = slug_query
            else:
                # No filtering at all, return default query
                queryset = Article.objects.all()
        return queryset
    
    class Meta:     
        API_LIMIT_PER_PAGE = 9
        queryset = Article.objects.all()
        resource_name = 'article/all'
        
        ordering = ['published_date']
        filtering = {
            'featured' : ('exact',),
            'published_date' : ('gte',),
        }
