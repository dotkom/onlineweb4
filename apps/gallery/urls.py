# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.gallery.views',
    url(r'^$', 'index', name='gallery_index'),
    url(r'^upload$', 'upload', name='gallery_upload'),
    url(r'^number_of_untreated$', 'number_of_untreated', name='number_of_untreated'),
    url(r'^delete_all$', 'delete_all', name='delete_all'),
#    url(r'^(?P<event_id>\d+)/attend/$', 'attendEvent', name='attend_event'),
)
