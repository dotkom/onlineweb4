# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.payment import views

urlpatterns = [
    url(r'^$', views.photoalbum, name='photoalbum'),
]
