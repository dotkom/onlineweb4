# -*- coding: utf-8 -*-

from apps.api.utils import SharedAPIRootRouter
from apps.gallery import views
from django.conf.urls import url

urlpatterns = [
    url(r'^upload/$', views.upload, name='gallery_upload'),
    url(r'^number_of_untreated/$', views.number_of_untreated, name='number_of_untreated'),
    url(r'^get_all_untreated/$', views.get_all_untreated, name='get_all_untreated'),
    url(r'^crop_image/$', views.crop_image, name='crop_image'),
    url(r'^all_images/', views.all_images, name='all_images'),
    url(r'^search/', views.search, name='search'),
]

# API v1

router = SharedAPIRootRouter()
router.register(r'images', views.ResponsiveImageViewSet)
