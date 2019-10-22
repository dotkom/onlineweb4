# -*- coding: utf-8 -*-
from django.urls import path

from apps.api.utils import SharedAPIRootRouter
from apps.photoalbum import views

urlpatterns = [
    path('', views.AlbumsListView.as_view(), name='albums_list'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name="album_detail"),
    path('album/<int:album_pk>/photo/<int:pk>/', views.PhotoDetailView.as_view(), name="photo_detail"),
]

# API v1
router = SharedAPIRootRouter()
router.register(r'photoalbum/albums', views.AlbumViewSet, basename='albums')
router.register(r'photoalbum/photos', views.PhotoViewSet, basename='album_photos')
router.register(r'photoalbum/tags', views.UserTagViewSet, basename='album_tags')
