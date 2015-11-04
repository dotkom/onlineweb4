# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.authentication.dashboard.views',
    url(r'^$', 'index', name='auth_index'),
    url(r'^members/$', 'members_index', name='members_index'),
    url(r'^members/(?P<pk>\d+)/$', 'members_detail', name='members_detail'),
    url(r'^members/new/$', 'members_new', name='members_new'),
    url(r'^groups/$', 'groups_index', name='groups_index'),
    url(r'^groups/(?P<pk>\d+)/$', 'groups_detail', name='groups_detail'),
)
