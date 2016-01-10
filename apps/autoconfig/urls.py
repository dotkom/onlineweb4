# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.autoconfig.views import autoconfig

urlpatterns = patterns(
    'apps.autoconfig.views',
    url(r'^config-v1.1.xml$', autoconfig),
)
