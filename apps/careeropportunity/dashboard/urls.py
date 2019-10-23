# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.careeropportunity.dashboard import views

urlpatterns = [
    url(r"^$", views.index, name="careeropportunity_dashboard_index"),
    url(r"^add/$", views.detail, name="careeropportunity_dashboard_add"),
    url(
        r"^(?P<opportunity_id>\d+)/detail",
        views.detail,
        name="careeropportunity_dashboard_edit",
    ),
    url(
        r"^(?P<opportunity_id>\d+)/delete",
        views.delete,
        name="careeropportunity_dashboard_delete",
    ),
]
