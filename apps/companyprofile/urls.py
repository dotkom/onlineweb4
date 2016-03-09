# -*- coding: utf-8 -*-

from apps.companyprofile import views
from django.conf.urls import url

urlpatterns = [
    url(r'^(?P<company_id>\d+)/$', views.details, name='company_details'),
]
