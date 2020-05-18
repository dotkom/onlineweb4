# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.offline import views

# API v1
urlpatterns = [url(r"^$", views.main, name="offline")]

router = SharedAPIRootRouter()
router.register("offline", views.OfflineIssueViewSet)
