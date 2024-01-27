# -*- encoding: utf-8 -*-

from django.urls import re_path

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.shop import views

urlpatterns = [
    re_path(
        r"^token/(?P<token>[\w-]+)/$",
        views.SetRFIDWebView.as_view(),
        name="shop_set_rfid",
    )
]


router = SharedAPIRootRouter()
router.register("inventory", views.InventoryViewSet, basename="shop_inventory")
