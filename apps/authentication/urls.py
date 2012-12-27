# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.authentication.views',
    url(r'^login/$', 'login', name='auth_login'),
    url(r'^logout/$', 'logout', name='auth_logout'),
    url(r'^register/$', 'register', name='auth_register'),
    url(r'^verify/(\w+)/$', 'verify', name='auth_verify'),
    url(r'^recover/$', 'recover', name='auth_recover'),
    url(r'^set_password/(\w+)/$', 'set_password', name='auth_set_password'),
)
