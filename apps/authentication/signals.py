# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.tasks import SynchronizeGroups


@receiver(post_save, sender=Group)
def trigger_group_syncer(sender, instance, created, **kwargs):
    """
    :param sender: The model that triggered this hook
    :param instance: The model instance triggering this hook
    :param created: True if the instance was created, False if the instance was updated

    Calls the SynchronizeGroups Task if a group is updated. (Not if it's the initial creation of a group)
    """

    if created:
        # If a new instance is created, we do not need to trigger group sync.
        pass
    else:
        SynchronizeGroups.run()
