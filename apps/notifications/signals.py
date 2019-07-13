import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def sync_order_line_subtotal_to_payment_price(sender, instance: Notification, created=False, **kwargs):
    if created:
        instance.dispatch()
