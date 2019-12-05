# -*- coding: utf-8 -*-
from apps.api.utils import SharedAPIRootRouter
from apps.payment import views

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register(
    "payment/relations", views.PaymentRelationViewSet, basename="payment_relations"
)
router.register(
    "payment/transactions",
    views.PaymentTransactionViewSet,
    basename="payment_transactions",
)
router.register(
    "payment/prices", views.PaymentPriceReadOnlyViewSet, basename="payment_prices"
)
router.register(
    "payment/delays", views.PaymentDelayReadOnlyViewSet, basename="payment_delays"
)
