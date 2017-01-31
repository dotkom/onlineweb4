# -*- coding: utf-8 -*-
import logging
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
# from django.db.models import signals
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

# from apps.authentication.models import OnlineUser
from apps.authentication.tasks import SynchronizeGroups

User = get_user_model()
logger = logging.getLogger('syncer.%s' % __name__)
sync_uuid = uuid.uuid1()


@receiver(post_save, sender=Group)
def trigger_group_syncer(sender, created=False, **kwargs):
    """
    :param sender: The model that triggered this hook
    :param instance: The model instance triggering this hook
    :param created: True if the instance was created, False if the instance was updated

    Calls the SynchronizeGroups Task if a group is updated. (Not if it's the initial creation of a group)
    """
    global sync_uuid

    if created:
        # If a new instance is created, we do not need to trigger group sync.
        pass
    else:
        # If sync is triggered by adding a user to group or a group to a user
        # then we need to detach the signal hook listening to m2m changes on
        # those models as they will trigger a recursive call to this method.
        if sender == User.groups.through:
            logger.debug('Disconnect m2m_changed signal hook with uuid %s before synchronizing groups' % sync_uuid)
            if m2m_changed.disconnect(sender=sender, dispatch_uid=sync_uuid):
                logger.debug('Signal with uuid %s disconnected' % sync_uuid)
                SynchronizeGroups.run()

            sync_uuid = uuid.uuid1()
            logger.debug('m2m_changed signal hook reconnected with uuid: %s' % sync_uuid)
            m2m_changed.connect(receiver=trigger_group_syncer, dispatch_uid=sync_uuid, sender=User.groups.through)
        else:
            SynchronizeGroups.run()


m2m_changed.connect(trigger_group_syncer, dispatch_uid=sync_uuid, sender=User.groups.through)
