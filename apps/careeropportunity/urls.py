# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.careeropportunity.views',
    url(r'^$', 'index', name='careeropportunity_index'),
    url(r'^(?P<opportunity_id>\d+)/$', 'details', name='careeropportunity_details'),
)
