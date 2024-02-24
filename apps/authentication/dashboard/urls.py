# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.authentication.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="auth_index"),
    re_path(r"^groups/$", views.groups_index, name="groups_index"),
    re_path(r"^groups/create/$", views.GroupCreateView.as_view(), name="groups_create"),
    re_path(r"^groups/(?P<pk>\d+)/$", views.groups_detail, name="groups_detail"),
]
