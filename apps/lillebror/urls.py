# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.lillebror import views


urlpatterns = [
    url(r'^all/$', views.all_user_data, name='all_user_data'),
]

