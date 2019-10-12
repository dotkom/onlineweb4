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
router.register(r'albums', views.AlbumViewSet, basename='albums')
router.register(r'albums/(?P<album_pk>\d+)/photos', views.AlbumPhotoViewSet, basename='album_photos')
router.register(
    prefix=r'albums/(?P<album_pk>\d+)/photos/(?P<photo_pk>\d+)/tags/',
    viewset=views.PhotoUserTagViewSet,
    basename='album_tags',
)
