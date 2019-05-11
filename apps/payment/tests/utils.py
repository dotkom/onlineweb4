from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent
from apps.payment.models import Payment, PaymentPrice


def generate_event_payment(event, price=100, *args, **kwargs):
    payment: Payment = G(
        Payment,
        object_id=event.id,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
        *args,
        **kwargs
    )
    G(PaymentPrice, payment=payment, price=price)
    return payment
