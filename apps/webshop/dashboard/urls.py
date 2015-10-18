# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from apps.webshop.dashboard import views

urlpatterns = patterns('apps.webshop.dashboard.views',
    url(r'^$', views.Overview.as_view(), name='dashboard_webshop'),
    url(r'^categories/$', views.Categories.as_view(), name='dashboard_webshop_categories'),
    url(r'^category/(?P<slug>\w+)$', views.CategoryEdit.as_view(), name='dashboard_webshop_category'),
    url(r'^category/$', views.CategoryAdd.as_view(), name='dashboard_webshop_category_new'),

    url(r'^category/(?P<category_slug>\w+)/product/new$', views.ProductCreate.as_view(), name='dashboard_webshop_product_new'),
    url(r'^product/(?P<slug>\w+)$', views.ProductUpdate.as_view(), name='dashboard_webshop_product'),
    url(r'^product/(?P<slug>\w+)/delete$', views.ProductDelete.as_view(), name='dashboard_webshop_product_delete'),
)
