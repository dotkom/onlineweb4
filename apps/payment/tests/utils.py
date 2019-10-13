from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G

from apps.events.models import AttendanceEvent
from apps.fiken.models import FikenAccount
from apps.payment.models import Payment, PaymentPrice


def add_price_to_payment(payment: Payment, price=200) -> PaymentPrice:
    return G(PaymentPrice, payment=payment, price=price)


def generate_event_payment(event, price=100, *args, **kwargs):
    fiken_account = create_fiken_account()
    payment: Payment = G(
        Payment,
        object_id=event.id,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
        fiken_account=fiken_account,
        *args,
        **kwargs
    )
    add_price_to_payment(payment, price)
    return payment


def create_fiken_account() -> FikenAccount:
    return G(FikenAccount, name='Fly', code='1225', identifier='fly')
