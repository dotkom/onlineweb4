# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.companyprofile.dashboard.views',
    url(r'^$', 'index', name='companyprofiles'),
    url(r'^new/$', 'new', name='companyprofile_new'),
    url(r'^(?P<pk>\d+)/$', 'detail', name='companyprofile_detail'),
    url(r'^(?P<pk>\d+)/delete/$', 'delete', name='companyprofile_delete'),
)
