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
    # Ugly fix to get user data for membership application
    re_path(
        r"^temp_gather_user_data/$",
        views.temp_gather_user_data,
        name="temp_gather_user_data",
    ),
    re_path(
        r"^cancel_application/(?P<application_id>\d+)/$",
        views.cancel_application,
        name="approval_cancel_application",
    ),
]
