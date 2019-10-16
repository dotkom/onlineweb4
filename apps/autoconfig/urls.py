# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.autoconfig.views import autoconfig

urlpatterns = [
    url(r'^config-v1.1.xml$', autoconfig),
]
