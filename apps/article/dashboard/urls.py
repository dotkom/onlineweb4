# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.article.dashboard.views',
    url(r'^$', 'article_index', name='dashboard_article_index'),
    url(r'^create/$', 'article_create_or_edit', name='dashboard_article_create'),
    url(r'^edit/(?P<article_id>\d+)/(?P<article_slug>[a-zA-Z0-9_-]+)$', 'article_create_or_edit', name='dashboard_article_edit'),

    url(r'^tag/$', 'tag_index', name='dashboard_tag_index'),
    url(r'^tag/create$', 'tag_create_or_edit', name='dashboard_tag_create'),
    url(r'^tag/edit/(?P<name>[^\.]+)/(?P<slug>[^\.]+)$', 'tag_create_or_edit', name='dashboard_tag_edit'),
)