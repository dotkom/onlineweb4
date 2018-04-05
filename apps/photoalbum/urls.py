# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum import views


urlpatterns = [
    url(r'^$', views.AlbumsListView.as_view(), name='albums_list'),
    url(r'^(?P<pk>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/$', views.AlbumDetailView.as_view(), name="album_detail"),
    url(r'^(?P<album_pk>\d+)/(?P<album_slug>[a-zA-Z0-9_-]+)/(?P<pk>\w+)/$', views.PhotoDetailView.as_view(), name="photo_detail"),
]
