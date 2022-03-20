# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.companyprofile.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="companyprofiles"),
    re_path(r"^new/$", views.new, name="companyprofile_new"),
    re_path(r"^(?P<pk>\d+)/$", views.detail, name="companyprofile_detail"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.delete, name="companyprofile_delete"),
]
