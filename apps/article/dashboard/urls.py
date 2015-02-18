# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.article.dashboard.views',
    url(r'^$', 'index', name='dashboard_article_index'),
    url(r'^$', 'article_create_or_edit', name='dashboard_article_create'),
    url(r'^$', 'article_create_or_edit', name='dashboard_article_edit'),

    url(r'^tag/$', 'tags_index', name='dashboard_tag_index'),
    url(r'^tag/create^$', 'tags_create_or_edit', name='dashboard_tag_create'),
    url(r'^tag/edit/(?P<name>[^\.]+)/(?P<slug>[^\.]+)$', 'tags_create_or_edit', name='dashboard_tag_edit'),
)