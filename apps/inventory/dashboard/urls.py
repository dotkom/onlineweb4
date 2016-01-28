# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.inventory.dashboard.views',
    url(r'^$', 'index', name='dashboard_inventory_index'),
    url(r'^new/$', 'new', name='dashboard_inventory_new'),
    url(r'^item/(?P<item_pk>\d+)/$', 'details', name='dashboard_inventory_details'),
    url(r'^item/(?P<item_pk>\d+)/delete/$', 'item_delete', name='dashboard_inventory_delete'),
    url(r'^item/(?P<item_pk>\d+)/batch/new/$', 'batch_new', name='dashboard_inventory_batch_new'),
    url(r'^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/$', 'batch', name='dashboard_inventory_batch'),
    url(r'^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/delete/$',
        'batch_delete',
        name='dashboard_inventory_batch_delete'),
)
