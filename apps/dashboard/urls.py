# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.dashboard import views

urlpatterns = [re_path("^$", views.index, name="dashboard_index")]
