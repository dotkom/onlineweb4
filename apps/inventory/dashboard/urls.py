# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.inventory.dashboard import views

urlpatterns = [
    url(r"^$", views.index, name="dashboard_inventory_index"),
    url(r"^statistics/$", views.statistics, name="dashboard_inventory_statistics"),
    url(
        r"^statistics/orders/$",
        views.order_statistics,
        name="dashboard_inventory_order_statistics",
    ),
    url(r"^category/$", views.category_index, name="dashboard_category_index"),
    url(
        r"^category/(?P<category_pk>\d+)/$",
        views.category_details,
        name="dashboard_category_details",
    ),
    url(r"^category/new/$", views.category_new, name="dashboard_category_new"),
    url(
        r"^category/(?P<category_pk>\d+)/delete/$",
        views.category_delete,
        name="dashboard_category_delete",
    ),
    url(r"^new/$", views.new, name="dashboard_inventory_new"),
    url(r"^item/(?P<item_pk>\d+)/$", views.details, name="dashboard_inventory_details"),
    url(
        r"^item/(?P<item_pk>\d+)/delete/$",
        views.item_delete,
        name="dashboard_inventory_delete",
    ),
    url(
        r"^item/(?P<item_pk>\d+)/change/$",
        views.item_change_availability,
        name="dashboard_inventory_change",
    ),
    url(
        r"^item/(?P<item_pk>\d+)/batch/new/$",
        views.batch_new,
        name="dashboard_inventory_batch_new",
    ),
    url(
        r"^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/$",
        views.batch,
        name="dashboard_inventory_batch",
    ),
    url(
        r"^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/delete/$",
        views.batch_delete,
        name="dashboard_inventory_batch_delete",
    ),
]
