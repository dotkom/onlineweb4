# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.photoalbum import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.create_album, name="create_album"),
    url(r'^(?P<title>\w+)/$', views.album, name="album")

]
