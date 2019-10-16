from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from . import status
from .models import PaymentReceipt, PaymentRelation, PaymentTransaction


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


@receiver(signal=post_save, sender=PaymentRelation)
@receiver(signal=post_save, sender=PaymentTransaction)
def send_receipt_after_payment(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(PaymentRelation)
    receipt_exists = PaymentReceipt.objects.filter(Q(object_id=instance.id) & Q(content_type=content_type)).exists()
    if instance.status == status.DONE and not receipt_exists:
        receipt = PaymentReceipt(object_id=instance.id, content_type=content_type)
        receipt.save()
