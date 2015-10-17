# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.careeropportunity.dashboard.views',
    url(r'^$', 'index', name='careeropportunity_dashboard_index'),
    url(r'^add/$', 'detail', name='careeropportunity_dashboard_add'),
    url(r'^(?P<opportunity_id>\d+)/detail', 'detail', name='careeropportunity_dashboard_edit'),
    url(r'^(?P<opportunity_id>\d+)/delete', 'delete', name='careeropportunity_dashboard_delete'),
)
