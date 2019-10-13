from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from apps.events.models import AttendanceEvent
from apps.payment.constants import StripeKey, TransactionType
from apps.payment.models import PaymentRelation, PaymentTransaction
from apps.webshop.models import OrderLine

from .constants import VatTypeSale
from .models import FikenAccount, FikenOrderLine, FikenSale
from .settings import NIBBLE_ACCOUNT_IDENTIFIER


def _get_nibble_account():
    try:
        return FikenAccount.objects.get(identifier=NIBBLE_ACCOUNT_IDENTIFIER)
    except FikenAccount.DoesNotExist:
        raise ImproperlyConfigured('Nibble account object does not exist')


def create_sale_from_transaction(transaction: PaymentTransaction, amount: int, sale_status: str) -> FikenSale:
    ore_amount = amount * 100  # Transaction amount is in Kr, sale amount is in øre
    nibble_account = _get_nibble_account()
    sale = FikenSale.objects.create(
        stripe_key=StripeKey.TRIKOM,
        original_amount=ore_amount,
        transaction_type=TransactionType.KIOSK,
        object_id=transaction.id,
        content_type=ContentType.objects.get_for_model(transaction),
        status=sale_status,
        customer=transaction.user,
    )
    FikenOrderLine.objects.create(
        sale=sale,
        description=f'{transaction.get_description()} - {transaction.user.get_full_name()}',
        price=ore_amount,
        vat_type=VatTypeSale.OUTSIDE,
        account=nibble_account,
    )
    return sale


def create_sale_from_relation(relation: PaymentRelation, amount: int, sale_status: str) -> FikenSale:
    ore_amount = amount * 100  # Payment price is in Kr, sale amount is in Øre
    sale = FikenSale.objects.create(
        stripe_key=relation.payment.stripe_key,
        original_amount=ore_amount,
        transaction_type=relation.payment.transaction_type,
        object_id=relation.id,
        content_type=ContentType.objects.get_for_model(relation),
        status=sale_status,
        customer=relation.user,
    )

    if relation.payment.is_type(AttendanceEvent):
        FikenOrderLine.objects.create(
            sale=sale,
            description=f'{relation.get_description()} - {relation.user.get_full_name()}',
            price=ore_amount,
            vat_type=VatTypeSale.OUTSIDE,
            account=relation.payment.fiken_account,
        )
    elif relation.payment.is_type(OrderLine):
        order_line: OrderLine = relation.payment.content_object
        for order in order_line.orders.all():
            FikenOrderLine.objects.create(
                sale=sale,
                description=f'{order_line} - {relation.user.get_full_name()}',
                price=order.price * 100,  # Webshop price is in Kr, Fiken price is in Øre
                vat_type=order.product.vat_type,
                account=order.product.fiken_account,
            )

    return sale
