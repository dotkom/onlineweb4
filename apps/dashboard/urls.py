# -*- coding: utf-8 -*-

from apps.dashboard import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='dashboard_index'),
]
