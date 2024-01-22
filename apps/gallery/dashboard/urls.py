# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.urls import re_path

from apps.gallery.dashboard import views

app_name = "gallery"

urlpatterns = [
    re_path(r"^$", views.GalleryIndex.as_view(), name="index"),
    re_path(r"^(?P<pk>\d+)/$", views.GalleryDetail.as_view(), name="detail"),
    re_path(r"^upload/$", views.GalleryUpload.as_view(), name="upload"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.GalleryDelete.as_view(), name="delete"),
    re_path(r"^unhandled/$", views.GalleryUnhandledIndex.as_view(), name="unhandled"),
    re_path(
        r"^unhandled/(?P<pk>\d+)/delete/$",
        views.GalleryUnhandledDelete.as_view(),
        name="unhandled_delete",
    ),
]
