# -*- encoding: utf-8 -*-

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.shop import views

urlpatterns = []


router = SharedAPIRootRouter()
router.register('orderline', views.OrderLineViewSet)
router.register('transactions', views.TransactionViewSet)
router.register('usersaldo', views.UserViewSet)
router.register('inventory', views.InventoryViewSet)
