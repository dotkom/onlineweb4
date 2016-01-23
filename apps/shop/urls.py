# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.shop import views

urlpatterns = patterns('',
        url(r'^rfid/$', views.SetRFIDView.as_view(), name='set_rfid')
)

# API v1
from apps.api.utils import SharedAPIRootRouter

router = SharedAPIRootRouter()
router.register('orderline', views.OrderLineViewSet)
router.register('transactions', views.TransactionViewSet)
router.register('usersaldo', views.UserViewSet)
router.register('inventory', views.InventoryViewSet)
