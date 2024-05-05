from django.urls import re_path

from apps.approval.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="approvals"),
    re_path(
        r"^approve_application/$",
        views.approve_application,
        name="approval_approve_application",
    ),
    re_path(
        r"^decline_application/$",
        views.decline_application,
        name="approval_decline_application",
    ),
]
