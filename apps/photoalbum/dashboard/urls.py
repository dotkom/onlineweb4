# -*- coding: utf8 -*-

from django.conf.urls import url

from apps.photoalbum.dashboard import views

urlpatterns = [
	url(r'^$', views.PhotoAlbumIndex.as_view(), name='dashboard_photoalbum_index'),
  url(r'^new/$', views.PhotoAlbumCreate.as_view(), name='dashboard_photoalbum_create'),
  url(r'^(?P<pk>\d+)/$', views.PhotoAlbumDetailDashboard.as_view(), name='dashboard_photoalbum_detail'),
  url(r'^(?P<pk>\d+)/edit/$', views.PhotoAlbumEdit.as_view(), name='dashboard_photoalbum_edit')
  

]