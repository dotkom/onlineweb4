# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.approval.dashboard.views',
    url(r'^$', 'index', name='approvals'),
    url(r'^approve_application/$', 'approve_application', name='approval_approve_application'),
    url(r'^decline_application/$', 'decline_application', name='approval_decline_application'),
)
