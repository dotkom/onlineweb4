# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.resourcecenter import views

urlpatterns = [
    url(r'^$', views.index, name='resourcecenter_index'),
]

router = SharedAPIRootRouter()
router.register('resources', views.ResourceViewSet)
