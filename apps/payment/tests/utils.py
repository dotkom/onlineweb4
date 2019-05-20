from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent
from apps.payment.models import Payment, PaymentPrice


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
