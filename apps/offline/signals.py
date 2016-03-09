# -*- coding: utf-8 -*-
from apps.offline.models import Issue
from apps.offline.tasks import create_thumbnail
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Issue)
def trigger_create_thumbnail(sender, instance, created, **kwargs):
    """
    :param sender: The model that triggered this hook
    :param instance: The model instance triggering this hook
    :param created: True if the instance was created, False if the instance was updated

    Calls the create thumbnail task if an issue saved (either created or updated).
    """

    create_thumbnail(instance)
