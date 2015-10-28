# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.conf.urls import patterns, url

from apps.gallery.dashboard.views import (
    GalleryIndex,
    GalleryDetail,
    GalleryUnhandledIndex,
    GalleryUpload,
    GalleryDelete,
    GalleryUnhandledDelete
)

urlpatterns = patterns(
    'apps.gallery.dashboard',
    url(
        '^$',
        GalleryIndex.as_view(),
        name='index'
    ),
    url(
        '^(?P<pk>\d+)/$',
        GalleryDetail.as_view(),
        name='detail'
    ),
    url(
        '^upload/$',
        GalleryUpload.as_view(),
        name='upload'
    ),
    url(
        '^(?P<pk>\d+)/delete/$',
        GalleryDelete.as_view(),
        name='delete'
    ),
    url(
        '^unhandled/$',
        GalleryUnhandledIndex.as_view(),
        name='unhandled'
    ),
    url(
        '^unhandled/(?P<pk>\d+)/delete/$',
        GalleryUnhandledDelete.as_view(),
        name='unhandled_delete'
    )
)
