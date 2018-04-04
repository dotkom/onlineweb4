# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum import views


urlpatterns = [
    url(r'^$', views.AlbumsListView.as_view(), name='albums_list'),
    url(r'^create$', views.create_album, name="create_album"),
    url(r'^edit/(?P<pk>\d+)/$', views.edit_album, name="edit_album"), 
    url(r'^delete/(?P<pk>\d+)$', views.delete_album, name="delete_album"),
    url(r'^edit/delete_photos/(?P<pk>\d+)', views.delete_photos, name="delete_photos"),
    url(r'^(?P<pk>\d+)/(?P<album_slug>[a-zA-Z0-9_-]+)/$', views.AlbumDetailView.as_view(), name="album_detail"),
    url(r'^(?P<album_pk>\d+)/(?P<album_slug>[a-zA-Z0-9_-]+)/(?P<pk>\w+)/$', views.PhotoDetailView.as_view(), name="photo_detail"),
]
