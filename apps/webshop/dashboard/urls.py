# -*- encoding: utf-8 -*-
from django.urls import re_path

from apps.webshop.dashboard import views

app_name = "webshop"

urlpatterns = [
    re_path(r"^$", views.Overview.as_view(), name="index"),
    re_path(r"^categories/$", views.Categories.as_view(), name="categories"),
    re_path(r"^category/new$", views.CategoryCreate.as_view(), name="category_new"),
    re_path(
        r"^category/(?P<slug>[-_\w]+)/view$",
        views.CategoryView.as_view(),
        name="category",
    ),
    re_path(
        r"^category/(?P<slug>[-_\w]+)/update$",
        views.CategoryUpdate.as_view(),
        name="category_update",
    ),
    re_path(
        r"^category/(?P<slug>[-_\w]+)/delete$",
        views.CategoryDelete.as_view(),
        name="category_delete",
    ),
    re_path(
        r"^category/(?P<category_slug>[-_\w]+)/product/new$",
        views.ProductCreate.as_view(),
        name="product_new",
    ),
    re_path(
        r"^product/(?P<slug>[-_\w]+)/view$", views.ProductView.as_view(), name="product"
    ),
    re_path(
        r"^product/(?P<slug>[-_\w]+)/update$",
        views.ProductUpdate.as_view(),
        name="product_update",
    ),
    re_path(
        r"^product/(?P<slug>[-_\w]+)/delete$",
        views.ProductDelete.as_view(),
        name="product_delete",
    ),
    re_path(
        r"^product/(?P<slug>[-_\w]+)/image$",
        views.ProductImage.as_view(),
        name="product_image",
    ),
    re_path(r"^orders/$", views.Orders.as_view(), name="orders"),
    re_path(r"^order/(?P<pk>\d+)$", views.Order.as_view(), name="order"),
    re_path(
        r"^order/(?P<pk>\d+)/deliver$",
        views.OrderDeliver.as_view(),
        name="order-deliver",
    ),
]
