# -*- coding: utf-8 -*-
from copy import copy

from django.template.defaultfilters import slugify
from unidecode import unidecode
from django.utils import timezone

from tastypie import fields
from tastypie.resources import ModelResource

from apps.api.v0.image import ImageResource
from apps.api.v0.authentication import UserResource
from apps.article.models import Article


class ArticleResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by', full=True)
    image = fields.ToOneField(ImageResource, 'image', full=True, null=True)

    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'articles'.
        if isinstance(data, dict):
            data['articles'] = copy(data['objects'])
            del(data['objects'])
        return data

    # Making multiple images for the article
    def dehydrate(self, bundle):

        # Setting slug-field
        bundle.data['slug'] = slugify(unidecode(bundle.data['heading']))

        # Returning washed object
        return bundle

    def get_object_list(self, request):
        # Getting the GET-params
        if 'tag' in request.GET:
            request_tag = request.GET['tag']
        else:
            request_tag = None

        if 'year' in request.GET:
            request_year = request.GET['year']
        else:
            request_year = None

        if 'month' in request.GET:
            request_month = request.GET['month']
        else:
            request_month = None

        # Check filtering here
        if request_year is not None:
            if request_month is not None:
                # Filtering on both year and month
                queryset = Article.objects.filter(
                    published_date__year=request_year, published_date__month=request_month,
                    published_date__lte=timezone.now()).order_by('-published_date')
            else:
                # Filtering on only year
                queryset = Article.objects.filter(
                    published_date__year=request_year,
                    published_date__lte=timezone.now()).order_by('-published_date')
        else:
            # Not filtering on year, check if filtering on slug (tag) or return default query
            if request_tag is not None:
                # Filtering on slug
                queryset = Article.objects.filter(
                    tags__name__in=[request_tag],
                    published_date__lte=timezone.now()
                ).order_by('-published_date')
            else:
                # No filtering at all, return default query
                queryset = Article.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        return queryset

    class Meta(object):
        API_LIMIT_PER_PAGE = 9
        queryset = Article.objects.filter(published_date__lte=timezone.now())
        resource_name = 'article/all'
        ordering = ['-published_date']
        include_absolute_url = True
        filtering = {
            'featured': ('exact',),
            'published_date': ('gte',),
        }


class ArticleLatestResource(ModelResource):
    author = fields.ToOneField(UserResource, 'created_by')

    class Meta(object):
        queryset = Article.objects.filter(published_date__lte=timezone.now())

        resource_name = 'article/latest'
        filtering = {
            'featured': ('exact',)
        }
        ordering = ['-published_date']
        max_limit = 25

    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'articles'.
        if isinstance(data, dict):
            data['articles'] = copy(data['objects'])
            del(data['objects'])
        return data

    def dehydrate(self, bundle):
        bundle.data['slug'] = slugify(unidecode(bundle.data['heading']))
        return bundle
