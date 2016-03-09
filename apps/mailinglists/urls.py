# -*- coding: utf-8 -*-

from apps.mailinglists import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='mailinglists_index')
]
