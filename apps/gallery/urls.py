# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.gallery import views
from apps.gallery.views import CropView, PresetView

app_name = "gallery"

urlpatterns = [
    re_path("^upload/$", views.upload, name="upload"),
    re_path("^unhandled/$", views.unhandled, name="unhandled"),
    re_path("^crop/$", CropView.as_view(), name="crop"),
    re_path("^all/", views.all_images, name="all"),
    re_path("^search/", views.search, name="search"),
    re_path("^preset/", PresetView.as_view(), name="preset"),
]

# API v1

router = SharedAPIRootRouter()
router.register(r"images", views.ResponsiveImageViewSet)
