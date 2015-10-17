# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.gallery.views',
    url(r'^upload$', 'upload', name='gallery_upload'),
    url(r'^number_of_untreated$', 'number_of_untreated', name='number_of_untreated'),
    url(r'^get_all_untreated$', 'get_all_untreated', name='get_all_untreated'),
    url(r'^crop_image$', 'crop_image', name='crop_image'),
    url(r'^all_images/', 'all_images', name='all_images'),
    url(r'^search/', 'search', name='search'),
)
