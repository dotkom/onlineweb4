# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.photoalbum import views

urlpatterns = [
    url(r'^$', views.AlbumsListView.as_view(), name='albums_list'),
    url(r'^(?P<pk>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/$', views.AlbumDetailView.as_view(), name="album_detail"),
    url(r'^(?P<album_pk>\d+)/(?P<album_slug>[a-zA-Z0-9_-]+)/(?P<pk>\w+)/$',
        views.PhotoDetailView.as_view(), name="photo_detail"),
]
# API v1
router = SharedAPIRootRouter()
router.register('albums', views.AlbumViewSet, basename='albums')
router.register('albums/<int:album_id>/photos', views.AlbumPhotoViewSet, basename='album_photos')
router.register('albums/<int:album_id>/photos/<int:photo_id>/tags/', views.PhotoUserTagViewSet, basename='album_photos')
