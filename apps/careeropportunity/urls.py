# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.careeropportunity import views

urlpatterns = [
    re_path(r"^$", views.index, name="careeropportunity_index"),
    re_path(r"^(\d+)/$", views.index, name="careeropportunity_details"),
]

# API v1
router = SharedAPIRootRouter()
router.register(r"career", views.CareerViewSet, basename="careeropportunity")
