from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Session
from .tasks import clear_session_task


@receiver(post_save, sender=Session)
def trigger_create_thumbnail(sender, instance: Session, created=False, **kwargs):
    """
    Call for deletion of a session a set time after the session is created.
    """
    if created:
        deletion_time = timezone.datetime.utcnow() + timezone.timedelta(minutes=30)
        clear_session_task.apply_async(
            kwargs={"session_id": instance.id}, eta=deletion_time
        )
