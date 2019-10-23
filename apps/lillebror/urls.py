# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.lillebror import views


urlpatterns = [
    url(r'^all/$', views.all_user_data, name='all_user_data'),
]


router = SharedAPIRootRouter()
router.register('lillebror', views.all_user_data, basename='all_user_data')
router.register('lillebror/deleteuser', views.RemoveUserDataAsDelete, basename='RemoveUserDataAsDelete')
