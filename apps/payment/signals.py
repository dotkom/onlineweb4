import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from . import status
from .models import FikenSale, PaymentRelation, PaymentTransaction
from .serializers import FikenSaleSerializer
from .tasks import register_sale_with_fiken

logger = logging.getLogger(__name__)


@receiver(signal=pre_save, sender=PaymentRelation)
def handle_payment_relation_status_change(sender, instance: PaymentRelation, **kwargs):
    if instance.status == status.SUCCEEDED:
        # Handle the completed payment. Remove delays, suspensions and marks
        instance.payment.handle_payment(instance.user)
        instance.status = status.DONE
    elif instance.status == status.REFUNDED:
        instance.refunded = True
        instance.payment.handle_refund(instance)
        instance.status = status.REMOVED


@receiver(signal=pre_save, sender=PaymentTransaction)
def handle_payment_transaction_status_change(sender, instance: PaymentTransaction, **kwargs):
    # When a payment succeeds, ot should be stored to the DB
    if instance.status == status.SUCCEEDED:
        instance.user.change_saldo(instance.amount)

        # Pass the transaction to the next step, which is DONE
        instance.status = status.DONE

    # Handle when a transaction is being refunded by Stripe
    if instance.status == status.REFUNDED:
        instance.user.change_saldo(-instance.amount)

        # Pass transaction to the next strip, which is REMOVED
        instance.status = status.REMOVED


@receiver(post_save, sender=FikenSale)
def handle_fiken_sale_created(sender, instance: FikenSale, created=False, **kwargs):
    if created:
        logger.info(f'Registering {instance} with Fiken')
        sale_data = FikenSaleSerializer(instance).data
        register_sale_with_fiken.delay(sale_data=sale_data)
    else:
        logger.warning(f'{instance} updated after creation')
