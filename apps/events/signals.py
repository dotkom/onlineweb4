# from django.db.models.signals import post_delete, post_save
# from django.dispatch import receiver

# from .models import Attendee, EventUserAction


# @receiver(signal=post_save, sender=Attendee)
# def handle_payment_relation_status_change(sender, instance: Attendee, **kwargs):
#     EventUserAction.objects.create(
#         user=instance.user, event=instance.event.event, type="register"
#     )


# @receiver(signal=post_delete, sender=Attendee)
# def handle_payment_transaction_status_change(sender, instance: Attendee, **kwargs):
#     EventUserAction.objects.create(
#         user=instance.user, event=instance.event.event, type="unregister"
#     )
