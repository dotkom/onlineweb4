# -*- coding: utf-8 -*-

from apps.careeropportunity import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='careeropportunity_index'),
    url(r'^(?P<opportunity_id>\d+)/$', views.details, name='careeropportunity_details'),
]
