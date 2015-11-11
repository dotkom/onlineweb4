# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.webshop.views import Home, CategoryDetail, ProductDetail, Checkout, RemoveOrder

urlpatterns = patterns('apps.webshop.views',
    url(r'^$', Home.as_view(), name='webshop_home'),
    url(r'^category/(?P<slug>[-\w]+)/$', CategoryDetail.as_view(), name='webshop_category'),
    url(r'^product/(?P<slug>[-\w]+)/$', ProductDetail.as_view(), name='webshop_product'),
    url(r'^checkout/$', Checkout.as_view(), name='webshop_checkout'),
    url(r'^remove/$', RemoveOrder.as_view(), name='webshop_remove_orders'),
)
