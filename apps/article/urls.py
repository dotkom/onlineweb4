# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.article import views

urlpatterns = [
    re_path(r"^archive/$", views.archive, name="article_archive"),
    re_path(
        r"^(?P<article_id>\d+)/(?P<article_slug>[a-zA-Z0-9_-]+)/$",
        views.details,
        name="article_details",
    ),
    re_path(r"^tag/(?P<slug>[^\.]+)/", views.archive_tag, name="view_article_tag"),
    re_path(r"^year/(?P<year>\d+)/$", views.archive_year, name="article_archive_year"),
    re_path(
        r"^year/(?P<year>\d+)/month/(?P<month>[^\.]+)/$",
        views.archive_month,
        name="article_archive_month",
    ),
]

router = SharedAPIRootRouter()
router.register(r"articles", views.ArticleViewSet)
