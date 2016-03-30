# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.careeropportunity import views

urlpatterns = [
    url(r'^$', views.index, name='careeropportunity_index'),
    url(r'^(?P<opportunity_id>\d+)/$', views.details, name='careeropportunity_details'),
]
