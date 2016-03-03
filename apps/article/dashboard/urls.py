# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.article.dashboard import views

urlpatterns = [
    url(r'^$', views.article_index, name='dashboard_article_index'),
    url(r'^new/$', views.article_create, name='dashboard_article_create'),
    url(r'^(?P<article_id>\d+)/$', views.article_detail, name='dashboard_article_detail'),
    url(r'^(?P<article_id>\d+)/edit/$', views.article_edit, name='dashboard_article_edit'),
]
