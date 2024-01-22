# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.dashboard import views

urlpatterns = [re_path(r"^$", views.index, name="dashboard_index")]
