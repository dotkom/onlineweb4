# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlineweb.apps.mailinglists.views',
    url(r'^$', 'index', name='mailinglists_index')
)
