from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AttendanceEvent, Event
from .notifications import EventUpdateNotification


@receiver(post_save, sender=Event)
def create_event_updated_notification(sender, instance: Event, created=False, **kwargs):
    """
    Send notifications to users updates to events
    """
    notification = EventUpdateNotification(event=instance)
    notification.dispatch()


@receiver(post_save, sender=AttendanceEvent)
def create_attendance_event_updated_notification(sender, instance: AttendanceEvent, created=False, **kwargs):
    """
    Send notifications to users updates to attendance events
    """
    notification = EventUpdateNotification(event=instance.event)
    notification.dispatch()
