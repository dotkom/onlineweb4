# -*- coding: utf-8 -*-
from apps.authentication.tasks import SynchronizeGroups
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=Group)
def trigger_group_syncer(sender, instance, created=False, **kwargs):
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

m2m_changed.connect(trigger_group_syncer, sender=User.groups.through)
