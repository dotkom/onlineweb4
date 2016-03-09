# -*- coding: utf-8 -*-

from apps.api.utils import SharedAPIRootRouter
from apps.article import views
from django.conf.urls import url

urlpatterns = [
    url(r'^archive/$', views.archive, name='article_archive'),
    url(r'^(?P<article_id>\d+)/(?P<article_slug>[a-zA-Z0-9_-]+)/$', views.details, name='article_details'),
    url(r'^tag/(?P<slug>[^\.]+)/', views.archive_tag, name='view_article_tag'),
    url(r'^year/(?P<year>\d+)/$', views.archive_year, name='article_archive_year'),
    url(r'^year/(?P<year>\d+)/month/(?P<month>[^\.]+)/$', views.archive_month, name='article_archive_month'),
]

router = SharedAPIRootRouter()
router.register(r'articles', views.ArticleViewSet)
