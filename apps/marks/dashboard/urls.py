# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.marks.dashboard.views',
    url(r'^$', 'index', name='marks_index'),
    url(r'^(?P<pk>\d+)/$', 'marks_details', name='marks_details'),
    url(r'^(?P<pk>\d+)/delete/$', 'marks_delete', name='marks_delete'),
    url(r'^(?P<pk>\d+)/edit/$', 'marks_edit', name='marks_edit'),
    url(r'^new/$', 'marks_new', name='marks_new'),
)
