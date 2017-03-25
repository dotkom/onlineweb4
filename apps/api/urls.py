# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from apps.events import views as event_views
from apps.shop import views as shop_views
from apps.sso import views as sso_views

urlpatterns = [
    url(r'^',       include('apps.api.v0.urls')),
    url(r'^',       include('apps.api.rfid.urls')),
    url(r'^v1/rfid/$', shop_views.SetRFIDView.as_view(), name='set_rfid'),
    url(r'^v1/auth/$', sso_views.TokenView.as_view(), name='oauth2_provider_token'),
    url(r'^v1/attend/$', event_views.AttendViewSet.as_view(), name='event_attend'),
]
