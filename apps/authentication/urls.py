# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.authentication import views

urlpatterns = [
    url(r'^login/$', views.login, name='auth_login'),
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^register/$', views.register, name='auth_register'),
    url(r'^verify/(?P<token>\w+)/$', views.verify, name='auth_verify'),
    url(r'^recover/$', views.recover, name='auth_recover'),
    url(r'^set_password/(?P<token>\w+)/$', views.set_password, name='auth_set_password'),
]
