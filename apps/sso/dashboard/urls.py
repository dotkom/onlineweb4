# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

from django.conf.urls import url

from .views import app_details, index, new_app

app_name = 'sso'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^app/new/', new_app, name='new_app'),
    url(r'^app/(?P<app_pk>\d+)/', app_details, name='app_details'),
]
