# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.resourcecenter.views',
    url(r'^$', 'index', name='resourcecenter_index'),
    url(r'^gameservers/$', 'gameservers', name='resourcecenter_gameservers'),
)
