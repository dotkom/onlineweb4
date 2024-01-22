# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.authentication.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="auth_index"),
    re_path(r"^groups/$", views.groups_index, name="groups_index"),
    re_path(r"^groups/create/$", views.GroupCreateView.as_view(), name="groups_create"),
    re_path(r"^groups/(?P<pk>\d+)/$", views.groups_detail, name="groups_detail"),
    re_path(r"^user/$", views.UserSearchView.as_view(), name="user_search"),
    re_path(r"^user/list/$", views.UserListView.as_view(), name="user_list"),
    re_path(
        r"^user/(?P<user_id>\d+)/$",
        views.UserDetailView.as_view(),
        name="dashboard_user_detail",
    ),
    re_path(
        r"^user/(?P<user_id>\d+)/edit$",
        views.UserUpdateView.as_view(),
        name="dashboard_user_edit",
    ),
    re_path(
        r"^user/(?P<user_id>\d+)/delete",
        views.UserDeleteView.as_view(),
        name="dashboard_user_delete",
    ),
]
