# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.mailinglists import views

urlpatterns = [
    url(r'^$', views.index, name='mailinglists_index')
]
