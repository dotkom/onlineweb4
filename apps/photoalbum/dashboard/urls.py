# -*- coding: utf8 -*-

from django.conf.urls import url

from apps.photoalbum.dashboard import views

urlpatterns = [
	url('$,' views.AlbumList.as_view(), name='album_list')
]