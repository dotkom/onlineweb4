# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.payment.views',
     url(r'^(?P<event_id>\d+)/(?P<payment_id>\d+)/$', 'payment', name='payment'),
     url(r'^payment_info/$', 'payment_info', name='payment_info'),
)