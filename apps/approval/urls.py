# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.approval.views',
    url(r'^send_fos_application/$', 'create_fos_application', name='approval_send_fos_application'),
    url(
        r'^send_membership_application/$',
        'create_membership_application',
        name='approval_send_membership_application'
    ),
    url(r'^cancel_application/(?P<application_id>\d+)/$', 'cancel_application', name='approval_cancel_application'),
)
