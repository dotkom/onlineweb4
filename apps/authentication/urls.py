# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.authentication import views
from apps.authentication.api import views as api_views

urlpatterns = [
    url(r'^login/$', views.login, name='auth_login'),
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^register/$', views.register, name='auth_register'),
    url(r'^verify/(?P<token>\w+)/$', views.verify, name='auth_verify'),
    url(r'^recover/$', views.recover, name='auth_recover'),
    url(r'^set_password/(?P<token>\w+)/$', views.set_password, name='auth_set_password'),
]

# API v1
router = SharedAPIRootRouter()
router.register('users', api_views.UserViewSet, base_name='users')
