import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent
from apps.payment.models import Payment, PaymentPrice

# Skip tests that require API-keys if the API-keys are not present
stripe_test = pytest.mark.skipif(
    settings.STRIPE_PUBLIC_KEYS["trikom"] == "pk_test_replace_this",
    reason="Stripe Test-API Keys not configured",
)


def add_price_to_payment(payment: Payment, price=200) -> PaymentPrice:
    return G(PaymentPrice, payment=payment, price=price)


def generate_event_payment(event, price=100, *args, **kwargs):
    payment: Payment = G(
        Payment,
        object_id=event.id,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
        *args,
        **kwargs
    )
    add_price_to_payment(payment, price)
    return payment
