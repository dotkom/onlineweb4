# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.resourcecenter import views

urlpatterns = [re_path(r"^$", views.index, name="resourcecenter_index")]

router = SharedAPIRootRouter()
router.register("resources", views.ResourceViewSet)
