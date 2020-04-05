# -*- encoding: utf-8 -*-

from django.conf.urls import url

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.shop import views

urlpatterns = [
    url(
        r"^token/(?P<token>[\w-]+)/$",
        views.SetRFIDWebView.as_view(),
        name="shop_set_rfid",
    )
]


router = SharedAPIRootRouter()
router.register("orderline", views.OrderLineViewSet, basename="shop_order_lines")
router.register("transactions", views.TransactionViewSet, basename="shop_transactions")
router.register("usersaldo", views.UserViewSet, basename="shop_saldo")
router.register("inventory", views.InventoryViewSet, basename="shop_inventory")
