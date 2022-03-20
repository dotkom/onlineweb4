# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.approval import views

urlpatterns = [
    re_path(
        r"^send_fos_application/$",
        views.create_fos_application,
        name="approval_send_fos_application",
    ),
    re_path(
        r"^send_membership_application/$",
        views.create_membership_application,
        name="approval_send_membership_application",
    ),
    re_path(
        r"^cancel_application/(?P<application_id>\d+)/$",
        views.cancel_application,
        name="approval_cancel_application",
    ),
]
