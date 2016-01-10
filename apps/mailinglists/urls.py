# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.mailinglists.views',
    url(r'^$', 'index', name='mailinglists_index')
)
