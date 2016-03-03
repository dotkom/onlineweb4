# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.companyprofile import views

urlpatterns = [
    url(r'^(?P<company_id>\d+)/$', views.details, name='company_details'),
]
