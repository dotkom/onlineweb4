# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.approval import views

urlpatterns = [
    url(
        r'^send_fos_application/$',
        views.create_fos_application,
        name='approval_send_fos_application'
    ),
    url(
        r'^send_membership_application/$',
        views.create_membership_application,
        name='approval_send_membership_application'
    ),
    url(
        r'^cancel_application/(?P<application_id>\d+)/$',
        views.cancel_application,
        name='approval_cancel_application'
    )
]
