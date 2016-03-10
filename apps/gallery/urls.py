# -*- coding: utf-8 -*-

from apps.api.utils import SharedAPIRootRouter
from apps.gallery import views
from django.conf.urls import url

urlpatterns = [
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^unhandled/$', views.unhandled, name='unhandled'),
    url(r'^crop/$', views.crop, name='crop'),
    url(r'^all/', views.all_images, name='all'),
    url(r'^search/', views.search, name='search'),
]

# API v1

router = SharedAPIRootRouter()
router.register(r'images', views.ResponsiveImageViewSet)
