# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.events.views',
    url(r'^(?P<event_id>\d+)/manage/$', 'index', name='events_index'),
)
