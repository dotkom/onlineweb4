# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.marks.dashboard.views',
    url(r'^$', 'index', name='marks_index'),
    url(r'^(?P<pk>\d+)/$', 'mark_details', name='mark_details'),
    url(r'^(?P<pk>\d+)/delete/$', 'mark_delete', name='mark_delete'),
    url(r'^(?P<pk>\d+)/edit/$', 'mark_edit', name='mark_edit'),
    url(r'^new/$', 'marks_new', name='marks_new'),
)
