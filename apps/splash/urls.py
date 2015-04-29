# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.splash.views',
    url(r'^$', 'index', name='splash_index'),
)