# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.dashboard.views',
    url(r'^$', 'index', name='dashboard_index'),
    url(r'^groups/$', 'group_index', name='group_index'),
    url(r'^groups/(?P<pk>\d+)/$', 'group_detail', name='group_detail'),
)
