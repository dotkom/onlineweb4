# -*- coding: utf-8 -*-
from apps.webshop import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='webshop_home'),
    url(r'^category/(?P<slug>[-\w]+)/$', views.CategoryDetail.as_view(), name='webshop_category'),
    url(r'^product/(?P<slug>[-\w]+)/$', views.ProductDetail.as_view(), name='webshop_product'),
    url(r'^checkout/$', views.Checkout.as_view(), name='webshop_checkout'),
    url(r'^remove/$', views.RemoveOrder.as_view(), name='webshop_remove_orders'),
]
