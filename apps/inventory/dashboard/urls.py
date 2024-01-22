# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.inventory.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="dashboard_inventory_index"),
    re_path(r"^discontinued", views.discontinued, name="dashboard_discontinued_index"),
    re_path(r"^statistics/$", views.statistics, name="dashboard_inventory_statistics"),
    re_path(
        r"^statistics/orders/$",
        views.order_statistics,
        name="dashboard_inventory_order_statistics",
    ),
    re_path(r"^category/$", views.category_index, name="dashboard_category_index"),
    re_path(
        r"^category/(?P<category_pk>\d+)/$",
        views.category_details,
        name="dashboard_category_details",
    ),
    re_path(r"^category/new/$", views.category_new, name="dashboard_category_new"),
    re_path(
        r"^category/(?P<category_pk>\d+)/delete/$",
        views.category_delete,
        name="dashboard_category_delete",
    ),
    re_path(r"^new/$", views.new, name="dashboard_inventory_new"),
    re_path(
        r"^item/(?P<item_pk>\d+)/$", views.details, name="dashboard_inventory_details"
    ),
    re_path(
        r"^item/(?P<item_pk>\d+)/delete/$",
        views.item_delete,
        name="dashboard_inventory_delete",
    ),
    re_path(
        r"^item/(?P<item_pk>\d+)/change/$",
        views.item_change_availability,
        name="dashboard_inventory_change",
    ),
    re_path(
        r"^item/(?P<item_pk>\d+)/batch/new/$",
        views.batch_new,
        name="dashboard_inventory_batch_new",
    ),
    re_path(
        r"^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/$",
        views.batch,
        name="dashboard_inventory_batch",
    ),
    re_path(
        r"^item/(?P<item_pk>\d+)/batch/(?P<batch_pk>\d+)/delete/$",
        views.batch_delete,
        name="dashboard_inventory_batch_delete",
    ),
]
