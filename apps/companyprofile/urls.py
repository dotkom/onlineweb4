# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.companyprofile import views

urlpatterns = [url(r"^(?P<company_id>\d+)/$", views.details, name="company_details")]

# API v1
router = SharedAPIRootRouter()
router.register("companies", views.CompanyViewSet, basename="companies")
