# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.resourcecenter import views

urlpatterns = [
    url(r'^$', views.index, name='resourcecenter_index'),
]
