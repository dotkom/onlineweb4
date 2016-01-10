# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.companyprofile.views',
    url(r'^(?P<company_id>\d+)/$', 'details', name='company_details'),
)
