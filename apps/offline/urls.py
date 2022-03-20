# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.offline import views

# API v1
urlpatterns = [re_path(r"^$", views.main, name="offline")]

router = SharedAPIRootRouter()
router.register("offline", views.OfflineIssueViewSet)
