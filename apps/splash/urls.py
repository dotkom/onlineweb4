# -*- coding: utf-8 -*-

from apps.splash import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='splash_index'),
    url(r'^events.ics$', views.calendar_export, name='splash_calendar'),
]
