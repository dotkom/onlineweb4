# -*- encoding: utf-8 -*-

from django.conf.urls import url
from django.urls import path

from apps.approval.dashboard import views

urlpatterns = [
    url(r"^$", views.index, name="approvals"),
    url(
        r"^approve_application/$",
        views.approve_application,
        name="approval_approve_application",
    ),
    url(
        r"^decline_application/$",
        views.decline_application,
        name="approval_decline_application",
    ),
    path(
        "application-periods/",
        views.ApplicationPeriodList.as_view(),
        name="application-periods-list",
    ),
    path(
        "application-periods/create/",
        views.ApplicationPeriodCreate.as_view(),
        name="application-periods-create",
    ),
    path(
        "application-periods/<int:pk>/",
        views.ApplicationPeriodDetail.as_view(),
        name="application-periods-detail",
    ),
    path(
        "application-periods/<int:pk>/update",
        views.ApplicationPeriodUpdate.as_view(),
        name="application-periods-update",
    ),
    path(
        "application-periods/<int:pk>/delete",
        views.ApplicationPeriodDelete.as_view(),
        name="application-periods-delete",
    ),
]
