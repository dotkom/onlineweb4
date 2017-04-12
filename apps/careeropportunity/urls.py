# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.careeropportunity import views

urlpatterns = [
    url(r'^$', views.index, name='careeropportunity_index'),
    url(r'^(?P<opportunity_id>\d+)/$', views.details, name='careeropportunity_details'),
]

# API v1
router = SharedAPIRootRouter()
router.register(r'career', views.CareerViewSet)
