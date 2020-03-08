# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [url(r"^$", views.index, name="index")]
