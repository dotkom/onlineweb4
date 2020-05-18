# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.marks.dashboard import views

urlpatterns = [
    url(r"^$", views.index, name="marks_index"),
    url(r"^(?P<pk>\d+)/$", views.marks_details, name="marks_details"),
    url(r"^(?P<pk>\d+)/delete/$", views.marks_delete, name="marks_delete"),
    url(r"^(?P<pk>\d+)/edit/$", views.marks_edit, name="marks_edit"),
    url(r"^new/$", views.marks_new, name="marks_new"),
]
