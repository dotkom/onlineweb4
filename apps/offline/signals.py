# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


from apps.offline.models import Issue
from apps.offline.tasks import create_thumbnail_task
from django.db import transaction


@receiver(post_save, sender=Issue)
def trigger_create_thumbnail(sender, instance: Issue, created=False, **kwargs):
    """
    Calls the create thumbnail task if an issue saved (either created or updated).
    """
    if not instance.image:
        transaction.on_commit(lambda: create_thumbnail_task.delay(issue_id=instance.id))
        
