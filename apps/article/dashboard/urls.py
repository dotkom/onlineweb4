# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.article.dashboard.views',
    url(r'^$', 'article_index', name='dashboard_article_index'),
    url(r'^new/$', 'article_create', name='dashboard_article_create'),
    url(r'^(?P<article_id>\d+)/$', 'article_detail', name='dashboard_article_detail'),
    url(r'^(?P<article_id>\d+)/edit/$', 'article_edit', name='dashboard_article_edit'),

    url(r'^tag/$', 'tag_index', name='dashboard_tag_index'),
    url(r'^tag/new/$', 'tag_create', name='dashboard_tag_create'),
    url(r'^tag/(?P<tag_id>\d+)/$', 'tag_edit', name='dashboard_tag_edit'),
)
