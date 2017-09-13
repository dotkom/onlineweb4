# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^1/$', views.test, name='test'),

]
