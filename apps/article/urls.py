# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.article.views',
    #url(r'^$', 'index', name='article_index'),
    url(r'^archive$', 'archive', name='article_archive'),
    url(r'^(?P<article_id>\d+)/$', 'details', name='article_details'),
    url(r'^tag/(?P<name>[^\.]+)/(?P<slug>[^\.]+)', 'archive_tag', name='view_article_tag'),
    url(r'^year/(?P<year>\d+)/$', 'archive_year', name='article_archive_year'),
    url(r'^year/(?P<year>\d+)/month/(?P<month>[^\.]+)/$', 'archive_month', name='article_archive_month'),
    url(r'^(?P<article_id>\d+)/(.*)$', 'details', name='article_details'), # Slug
)