# -*- coding: utf-8 -*-

from apps.autoconfig.views import autoconfig
from django.conf.urls import url

urlpatterns = [
    url(r'^config-v1.1.xml$', autoconfig),
]
