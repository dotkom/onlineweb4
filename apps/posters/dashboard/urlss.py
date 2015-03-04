# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.posters.dashboard.views',
    url(r'^$', 'posters_index', name='posters'),
    url(r'^add/$', 'posters_add', name='posters_add'),
    url(r'^view/$', 'posters_view', name='posters_view'),
)
