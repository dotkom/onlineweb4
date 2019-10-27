# -*- coding: utf-8 -*-
from apps.api.utils import SharedAPIRootRouter
from apps.photoalbum import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register(r"photoalbum/albums", views.AlbumViewSet, basename="albums")
router.register(r"photoalbum/photos", views.PhotoViewSet, basename="album_photos")
router.register(r"photoalbum/tags", views.UserTagViewSet, basename="album_tags")
