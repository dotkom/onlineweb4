# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum.dashboard import views

urlpatterns = [
    # url(r'^$', views.PhotoAlbumIndex.as_view(), name='dashboard_photoalbum_index'),
    url(r'^$', views.photoalbum_index, name='dashboard_photoalbum_index'),

    # url(r'^new/$', views.PhotoAlbumCreate.as_view(), name='dashboard_photoalbum_create'),
    url(r'^new/$', views.photoalbum_create, name='dashboard_photoalbum_create'),

    # url(r'^(?P<pk>\d+)/$', views.PhotoAlbumDetailDashboard.as_view(), name='dashboard_photoalbum_detail'),
    url(r'^(?P<pk>\d+)/$', views.photoalbum_detail, name='dashboard_photoalbum_detail'),

    # url(r'^(?P<pk>\d+)/edit/$', views.PhotoAlbumEdit.as_view(), name='dashboard_photoalbum_edit')
    url(r'^(?P<pk>\d+)/edit/$', views.photoalbum_edit, name='dashboard_photoalbum_edit'),

    url(r'^upload_photos/$', views.upload_photos, name='upload_photos')

]
