# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
)

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.shop import views

router = SharedAPIRootRouter()
router.register('orderline', views.OrderLineViewSet)
router.register('transactions', views.TransactionViewSet)
router.register('usersaldo', views.UserViewSet)