# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.userprofile.views',
    url(r'^$', 'index', name='profile'),
)
