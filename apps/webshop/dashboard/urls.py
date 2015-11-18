# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from apps.webshop.dashboard import views

urlpatterns = patterns('apps.webshop.dashboard.views',
    url(r'^$', views.Overview.as_view(), name='index'),
    url(r'^categories/$', views.Categories.as_view(), name='categories'),
    url(r'^category/new$', views.CategoryCreate.as_view(), name='category_new'),
    url(r'^category/(?P<slug>\w+)/view$', views.CategoryView.as_view(), name='category'),
    url(r'^category/(?P<slug>\w+)/update$', views.CategoryUpdate.as_view(), name='category_update'),
    url(r'^category/(?P<slug>\w+)/delete$', views.CategoryDelete.as_view(), name='category_delete'),

    url(r'^category/(?P<category_slug>\w+)/product/new$', views.ProductCreate.as_view(), name='product_new'),
    url(r'^product/(?P<slug>\w+)/view$', views.ProductView.as_view(), name='product'),
    url(r'^product/(?P<slug>\w+)/update$', views.ProductUpdate.as_view(), name='product_update'),
    url(r'^product/(?P<slug>\w+)/delete$', views.ProductDelete.as_view(), name='product_delete'),
    url(r'^product/(?P<slug>\w+)/image$', views.ProductImage.as_view(), name='product_image'),
    url(r'^orders/$', views.Orders.as_view(), name='orders'),
)
