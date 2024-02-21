from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Attendee, EventUserAction


@receiver(signal=pre_save, sender=Attendee)
def handle_payment_relation_status_change(sender, instance: Attendee, **kwargs):
    EventUserAction.objects.create(
        user=instance.user, event=instance.event, type="register"
    )


@receiver(signal=pre_delete, sender=Attendee)
def handle_payment_transaction_status_change(sender, instance: Attendee, **kwargs):
    EventUserAction.objects.create(
        user=instance.user, event=instance.event, type="unregister"
    )
