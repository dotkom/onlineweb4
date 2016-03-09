# -*- encoding: utf-8 -*-

from apps.approval.dashboard import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='approvals'),
    url(r'^approve_application/$', views.approve_application, name='approval_approve_application'),
    url(r'^decline_application/$', views.decline_application, name='approval_decline_application'),
]
