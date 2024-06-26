import logging
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.dispatch import receiver

from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.tasks import (
    SynchronizeGroups,
    assign_permission_from_group_admins,
)
from apps.gsuite.mail_syncer.main import update_g_suite_group, update_g_suite_user
from utils.disable_for_loaddata import disable_for_loaddata

User = get_user_model()
logger = logging.getLogger(f"syncer.{__name__}")
sync_uuid = uuid.uuid1()

MAILING_LIST_USER_FIELDS_TO_LIST_NAME = settings.MAILING_LIST_USER_FIELDS_TO_LIST_NAME


def run_group_syncer(user: User) -> None:
    """
    Tasks to run after User is changed.
    :param user: The user instance to sync groups for.
    """
    SynchronizeGroups.run()
    if settings.OW4_GSUITE_SYNC.get("ENABLED", False):
        ow4_gsuite_domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")
        if isinstance(user, User):
            logger.debug(f"Running G Suite syncer for user {user}")
            update_g_suite_user(ow4_gsuite_domain, user, suppress_http_errors=True)
        elif isinstance(user, Group):
            group = user
            logger.debug(f"Running G Suite syncer for group {group}")
            update_g_suite_group(
                ow4_gsuite_domain, group.name, suppress_http_errors=True
            )


@receiver(post_save, sender=Group)
@disable_for_loaddata
def trigger_group_syncer(sender, instance: Group, created=False, **kwargs):
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
            logger.debug(
                f"Disconnect m2m_changed signal hook with uuid {sync_uuid} before synchronizing groups"
            )
            if m2m_changed.disconnect(sender=sender, dispatch_uid=sync_uuid):
                logger.debug(f"Signal with uuid {sync_uuid} disconnected")
                run_group_syncer(instance)

            sync_uuid = uuid.uuid1()
            logger.debug(f"m2m_changed signal hook reconnected with uuid: {sync_uuid}")
            m2m_changed.connect(
                receiver=trigger_group_syncer,
                dispatch_uid=sync_uuid,
                sender=User.groups.through,
            )
        else:
            run_group_syncer(instance)


m2m_changed.connect(
    trigger_group_syncer, dispatch_uid=sync_uuid, sender=User.groups.through
)


@receiver(post_save, sender=GroupMember)
@disable_for_loaddata
def add_online_group_member_to_django_group(
    sender, instance: GroupMember, created=False, **kwargs
):
    online_group: OnlineGroup = instance.group
    group: Group = online_group.group
    user: User = instance.user
    if user not in group.user_set.all():
        group.user_set.add(user)


@receiver(pre_delete, sender=GroupMember)
def remove_online_group_members_from_django_group(
    sender, instance: GroupMember, **kwargs
):
    online_group: OnlineGroup = instance.group
    group: Group = online_group.group
    user: User = instance.user
    if user in group.user_set.all():
        group.user_set.remove(user)


@receiver(post_delete, sender=GroupMember)
@receiver(post_save, sender=GroupMember)
@disable_for_loaddata
def set_staff_status(sender, instance: GroupMember, created=False, **kwargs):
    """
    Set the staff status of the user whenever one of their group member relations are updated.
    This will resolve all the all the current member relations for the user to check if they are in
    a committee.
    TODO: Define staff status as a separate field on the OnlineGroup, as non-committee members may be staff.
    """
    user = instance.user
    should_user_be_staff = user.is_committee
    user.is_staff = should_user_be_staff
    user.save()


@disable_for_loaddata
def assign_group_perms(sender, instance, created=False, **kwargs):
    if isinstance(instance, GroupMember):
        assign_permission_from_group_admins(group_id=instance.group.id)
    if isinstance(instance, OnlineGroup):
        assign_permission_from_group_admins(group_id=instance.id)


m2m_changed.connect(assign_group_perms, sender=GroupRole.memberships.through)
m2m_changed.connect(assign_group_perms, sender=GroupRole.admin_for_groups.through)
