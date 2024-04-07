from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from utils.disable_for_loaddata import disable_for_loaddata

from . import status
from .models import PaymentReceipt, PaymentRelation


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


@receiver(signal=post_save, sender=PaymentRelation)
@disable_for_loaddata
def send_receipt_after_payment(sender, instance: PaymentRelation, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    receipt_exists = PaymentReceipt.objects.filter(
        Q(object_id=instance.id) & Q(content_type=content_type)
    ).exists()

    should_send_receipt = (
        instance.create_receipt
        and instance.status == status.DONE
        and not receipt_exists
    )
    if should_send_receipt:
        receipt = PaymentReceipt(object_id=instance.id, content_type=content_type)
        receipt.save()
