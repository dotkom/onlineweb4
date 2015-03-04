# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.posters.dashboard.views',
    url(r'^add/$', 'add', name='posters_add'),
    url(r'^view/$', 'view', name='posters_view'),
    url(r'^overview/$', 'overview', name='posters_overview'),
)
