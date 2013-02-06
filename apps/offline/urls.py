# -*- encoding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from onlineweb.apps.offline.views import main

urlpatterns = patterns('onlineweb.apps.offline.views',
    url(r'^$', 'main', name='offline')
)
