# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.autoconfig.views import autoconfig

urlpatterns = [re_path(r"^config-v1.1.xml$", autoconfig)]
