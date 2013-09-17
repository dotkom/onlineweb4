# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.offline.views import main

urlpatterns = patterns('apps.offline.views',
    url(r'^$', 'main', name='offline')
)
