# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.dashboard import views

urlpatterns = [url(r"^$", views.index, name="dashboard_index")]
