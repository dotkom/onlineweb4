# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.inventory.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='dashboard_inventory_index'),
    url(r'^new/$', views.new, name='dashboard_inventory_new'),
    url(r'^item/(?P<item_pk>\d+)/$', views.details, name='dashboard_inventory_details'),
    url(r'^item/(?P<item_pk>\d+)/delete/$', views.item_delete, name='dashboard_inventory_delete'),
    url(r'^item/(?P<item_pk>\d+)/batch/new/$', views.batch_new, name='dashboard_inventory_batch_new'),
    url(r'^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/$', views.batch, name='dashboard_inventory_batch'),
    url(r'^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/delete/$',
        views.batch_delete,
        name='dashboard_inventory_batch_delete'),
]
