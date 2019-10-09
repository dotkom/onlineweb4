# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.shop import views as shop_views
from apps.sso import views as sso_views

urlpatterns = [
    url(r'^v1/rfid/$', shop_views.SetRFIDView.as_view(), name='set_rfid'),
    url(r'^v1/auth/$', sso_views.TokenView.as_view(), name='oauth2_provider_token'),
]
