# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.conf.urls import patterns, url
from guardian.decorators import permission_required

from apps.gallery.dashboard.views import GalleryIndex, GalleryUnhandledIndex

urlpatterns = patterns(
    'apps.gallery.dashboard',
    url(
        '^$',
        (permission_required('gallery.view_responsiveimage'))(GalleryIndex.as_view()),
        name='index'
    ),
    url(
        '^unhandled/$',
        (permission_required('gallery.view_unhandledimage'))(GalleryUnhandledIndex.as_view()),
        name='unhandled_index'
    )
)
