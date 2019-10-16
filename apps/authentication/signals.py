# -*- coding: utf-8 -*-
import logging
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from apps.authentication.models import GroupMember, OnlineGroup
from apps.authentication.tasks import SynchronizeGroups
from apps.gsuite.mail_syncer.main import update_g_suite_group, update_g_suite_user

User = get_user_model()
logger = logging.getLogger('syncer.%s' % __name__)
sync_uuid = uuid.uuid1()


def run_group_syncer(user):
    """
    Tasks to run after User is changed.
    :param user: The user instance to sync groups for.
    :type user: OnlineUser
    :return: None
    """
    SynchronizeGroups.run()
    if settings.OW4_GSUITE_SYNC.get('ENABLED', False):
        ow4_gsuite_domain = settings.OW4_GSUITE_SYNC.get('DOMAIN')
        if isinstance(user, User):
            logger.debug('Running G Suite syncer for user {}'.format(user))
            update_g_suite_user(ow4_gsuite_domain, user, suppress_http_errors=True)
        elif isinstance(user, Group):
            group = user
            logger.debug('Running G Suite syncer for group {}'.format(group))
            update_g_suite_group(ow4_gsuite_domain, group.name, suppress_http_errors=True)


@receiver(post_save, sender=Group)
def trigger_group_syncer(sender, instance, created=False, **kwargs):
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
                run_group_syncer(instance)

            sync_uuid = uuid.uuid1()
            logger.debug('m2m_changed signal hook reconnected with uuid: %s' % sync_uuid)
            m2m_changed.connect(receiver=trigger_group_syncer, dispatch_uid=sync_uuid, sender=User.groups.through)
        else:
            run_group_syncer(instance)


m2m_changed.connect(trigger_group_syncer, dispatch_uid=sync_uuid, sender=User.groups.through)


@receiver(post_save, sender=GroupMember)
def add_online_group_member_to_django_group(sender, instance: GroupMember, created=False, **kwargs):
    online_group: OnlineGroup = instance.group
    group: Group = online_group.group
    user: User = instance.user
    if user not in group.user_set.all():
        group.user_set.add(user)


@receiver(pre_delete, sender=GroupMember)
def remove_online_group_members_from_django_group(sender, instance: GroupMember, **kwargs):
    online_group: OnlineGroup = instance.group
    group: Group = online_group.group
    user: User = instance.user
    if user in group.user_set.all():
        group.user_set.remove(user)
