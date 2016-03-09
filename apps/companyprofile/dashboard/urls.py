# -*- coding: utf-8 -*-

from apps.companyprofile.dashboard import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='companyprofiles'),
    url(r'^new/$', views.new, name='companyprofile_new'),
    url(r'^(?P<pk>\d+)/$', views.detail, name='companyprofile_detail'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='companyprofile_delete'),
]
