# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

from django.urls import re_path

from .views import app_details, index, new_app

app_name = "sso"

urlpatterns = [
    re_path(r"^$", index, name="index"),
    re_path(r"^app/new/", new_app, name="new_app"),
    re_path(r"^app/(?P<app_pk>\d+)/", app_details, name="app_details"),
]
