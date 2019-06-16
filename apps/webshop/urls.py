# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.webshop import views

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='webshop_home'),
    url(r'^category/(?P<slug>[-\w]+)/$', views.CategoryDetail.as_view(), name='webshop_category'),
    url(r'^product/(?P<slug>[-\w]+)/$', views.ProductDetail.as_view(), name='webshop_product'),
    url(r'^checkout/$', views.Checkout.as_view(), name='webshop_checkout'),
    url(r'^remove/$', views.RemoveOrder.as_view(), name='webshop_remove_orders'),
]

# API v1
router = SharedAPIRootRouter()
router.register('webshop/orders', views.OrderViewSet, basename='webshop_orders')
router.register('webshop/orderlines', views.OrderLineViewSet, basename='webshop_orderlines')
router.register('webshop/products', views.ProductViewSet, basename='webshop_products')
