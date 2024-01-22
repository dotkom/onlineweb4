# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.article.dashboard import views

urlpatterns = [
    re_path(r"^$", views.article_index, name="dashboard_article_index"),
    re_path(r"^new/$", views.article_create, name="dashboard_article_create"),
    re_path(
        r"^(?P<article_id>\d+)/$", views.article_detail, name="dashboard_article_detail"
    ),
    re_path(
        r"^(?P<article_id>\d+)/edit/$",
        views.article_edit,
        name="dashboard_article_edit",
    ),
]
