# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.marks.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="marks_index"),
    re_path(r"^(?P<pk>\d+)/$", views.marks_details, name="marks_details"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.marks_delete, name="marks_delete"),
    re_path(r"^(?P<pk>\d+)/edit/$", views.marks_edit, name="marks_edit"),
    re_path(r"^new/$", views.marks_new, name="marks_new"),
]
