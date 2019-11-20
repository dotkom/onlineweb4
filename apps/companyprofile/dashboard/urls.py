# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.companyprofile.dashboard import views

urlpatterns = [
    url(r"^$", views.index, name="companyprofiles"),
    url(r"^new/$", views.new, name="companyprofile_new"),
    url(r"^(?P<pk>\d+)/$", views.detail, name="companyprofile_detail"),
    url(r"^(?P<pk>\d+)/delete/$", views.delete, name="companyprofile_delete"),
]
