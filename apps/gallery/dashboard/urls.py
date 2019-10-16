# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.conf.urls import url

from apps.gallery.dashboard import views

app_name = 'gallery'

urlpatterns = [
    url(
        '^$',
        views.GalleryIndex.as_view(),
        name='index'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        views.GalleryDetail.as_view(),
        name='detail'
    ),
    url(
        '^upload/$',
        views.GalleryUpload.as_view(),
        name='upload'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        views.GalleryDelete.as_view(),
        name='delete'
    ),
    url(
        '^unhandled/$',
        views.GalleryUnhandledIndex.as_view(),
        name='unhandled'
    ),
    url(
        r'^unhandled/(?P<pk>\d+)/delete/$',
        views.GalleryUnhandledDelete.as_view(),
        name='unhandled_delete'
    )
]
