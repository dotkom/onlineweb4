# -*- coding: utf-8 -*-

from apps.shop import views as shop_views
from apps.sso import views as auth_views
from django.conf.urls import include, url

urlpatterns = [
    url(r'^',       include('apps.api.v0.urls')),
    url(r'^',       include('apps.api.rfid.urls')),
    url(r'^v1/rfid/$', shop_views.SetRFIDView.as_view(), name='set_rfid'),
    url(r'^v1/auth/$', auth_views.TokenView.as_view(), name='oauth2_provider_token'),
]
