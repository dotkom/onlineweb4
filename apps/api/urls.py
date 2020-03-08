# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.shop import views as shop_views

urlpatterns = [url(r"^v1/rfid/$", shop_views.SetRFIDView.as_view(), name="set_rfid")]
