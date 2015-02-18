# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.article.dashboard.views',
    url(r'^$', 'article_index', name='dashboard_article_index'),
    url(r'^create/$', 'article_create', name='dashboard_article_create'),
    url(r'^change/(?P<article_id>\d+)/$', 'article_change', name='dashboard_article_change'),

    url(r'^tag/$', 'tag_index', name='dashboard_tag_index'),
    url(r'^tag/create/$', 'tag_create', name='dashboard_tag_create'),
    url(r'^tag/change/(?P<tag_id>\d+)/$', 'tag_change', name='dashboard_tag_change'),
)