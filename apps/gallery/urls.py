# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.gallery import views
from apps.gallery.views import CropView, PresetView

app_name = "gallery"

urlpatterns = [
    re_path(r"^upload/$", views.upload, name="upload"),
    re_path(r"^unhandled/$", views.unhandled, name="unhandled"),
    re_path(r"^crop/$", CropView.as_view(), name="crop"),
    re_path(r"^all/", views.all_images, name="all"),
    re_path(r"^search/", views.search, name="search"),
    re_path(r"^preset/", PresetView.as_view(), name="preset"),
]

# API v1

router = SharedAPIRootRouter()
router.register(r"images", views.ResponsiveImageViewSet)
