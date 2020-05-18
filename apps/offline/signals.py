# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.offline.models import Issue
<<<<<<< HEAD
from apps.offline.notifications import OfflineCreatedNotification
from apps.offline.tasks import create_thumbnail
=======
from apps.offline.tasks import create_thumbnail_task
>>>>>>> develop


@receiver(post_save, sender=Issue)
def trigger_create_thumbnail(sender, instance: Issue, created=False, **kwargs):
    """
    Calls the create thumbnail task if an issue saved (either created or updated).
    """
<<<<<<< HEAD

    create_thumbnail(instance)


@receiver(post_save, sender=Issue)
def create_offline_created_notification(sender, instance, created=False, **kwargs):
    """
    Send notifications to users about a new release of Offline
    """
    if created:
        notification = OfflineCreatedNotification(issue=instance)
        notification.dispatch()
=======
    if not instance.image:
        create_thumbnail_task.delay(issue_id=instance.id)
>>>>>>> develop
