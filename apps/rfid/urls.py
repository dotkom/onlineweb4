# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.rfid.views',
    url(r'^', 'rfid', name='rfid'),
)
