# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.careeropportunity.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="careeropportunity_dashboard_index"),
    re_path(r"^add/$", views.detail, name="careeropportunity_dashboard_add"),
    re_path(
        r"^(?P<opportunity_id>\d+)/detail",
        views.detail,
        name="careeropportunity_dashboard_edit",
    ),
    re_path(
        r"^(?P<opportunity_id>\d+)/delete",
        views.delete,
        name="careeropportunity_dashboard_delete",
    ),
]
