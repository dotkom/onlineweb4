# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.posters.dashboard.views',
    url(r'^$', 'index', name='posters'),
    url(r'^add/$', 'add', name='posters_add'),
    url(r'^details/$', 'details', name='posters_details'),
)
