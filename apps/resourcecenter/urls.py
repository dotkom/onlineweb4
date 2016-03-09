# -*- coding: utf-8 -*-

from apps.resourcecenter import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='resourcecenter_index'),
    url(r'^gameservers/$', views.gameservers, name='resourcecenter_gameservers'),
]
