# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum import views


urlpatterns = [
    url(r'^$', views.AlbumsListView.as_view(), name='albums_list'),
    url(r'^create$', views.create_album, name="create_album"),
    url(r'^delete(?P<pk>\d+)$', views.delete_album, name="delete_album"),
    url(r'^(?P<pk>\w+)/$', views.AlbumDetailView.as_view(), name="album_detail"),
    # Should have album-name before pk
    url(r'^(?P<album_pk>\w+)/(?P<pk>\w+)/$', views.PhotoDetailView.as_view(), name="photo_detail"),

]
