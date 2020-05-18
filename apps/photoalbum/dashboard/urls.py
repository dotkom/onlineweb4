# -*- coding: utf-8 -*-
from django.urls import path

from apps.photoalbum.dashboard import views

app_name = "photoalbum"

urlpatterns = [
    path("", views.Overview.as_view(), name="index"),
    path("albums/", views.AlbumsView.as_view(), name="albums"),
    path("album/new", views.AlbumCreate.as_view(), name="album_new"),
    path("album/<int:pk>/view", views.AlbumView.as_view(), name="album"),
    path("album/<int:pk>/update", views.AlbumUpdate.as_view(), name="album_update"),
    path("album/<int:pk>/delete", views.AlbumDelete.as_view(), name="album_delete"),
    path(
        "album/<int:album_pk>/photo/new", views.PhotoCreate.as_view(), name="photo_new"
    ),
    path(
        "album/<int:album_pk>/photo/<int:pk>/update",
        views.PhotoUpdate.as_view(),
        name="photo_update",
    ),
    path(
        "album/<int:album_pk>/photo/<int:pk>/delete",
        views.PhotoDelete.as_view(),
        name="photo_delete",
    ),
]
