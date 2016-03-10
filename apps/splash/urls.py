# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.splash import views

urlpatterns = [
    url(r'^$', views.index, name='splash_index'),
    url(r'^events.ics$', views.calendar_export, name='splash_calendar'),
]
