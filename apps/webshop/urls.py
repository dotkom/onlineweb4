# -*- coding: utf-8 -*-
from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.webshop import views

urlpatterns = [
    re_path(r"^$", views.Home.as_view(), name="webshop_home"),
    re_path(
        r"^category/(?P<slug>[-\w]+)/$",
        views.CategoryDetail.as_view(),
        name="webshop_category",
    ),
    re_path(
        r"^product/(?P<slug>[-\w]+)/$",
        views.ProductDetail.as_view(),
        name="webshop_product",
    ),
    re_path(r"^checkout/$", views.Checkout.as_view(), name="webshop_checkout"),
    re_path(r"^remove/$", views.RemoveOrder.as_view(), name="webshop_remove_orders"),
]

# API v1
router = SharedAPIRootRouter()
router.register("webshop/orders", views.OrderViewSet, basename="webshop_orders")
router.register(
    "webshop/orderlines", views.OrderLineViewSet, basename="webshop_orderlines"
)
router.register("webshop/products", views.ProductViewSet, basename="webshop_products")
