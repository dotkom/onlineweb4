import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_delete, post_save, pre_delete
from django.dispatch import receiver

from apps.gsuite.models import GsuiteAlias, GsuiteGroup

from .tasks import (update_mailing_list, create_gsuite_group_task, update_gsuite_group_task, delete_gsuite_group_task,
                    update_gsuite_alias_task, delete_gsuite_alias_task, create_gsuite_alias_task)

User = get_user_model()

MAILING_LIST_USER_FIELDS_TO_LIST_NAME = {
    'infomail': 'info',
    'jobmail': 'oppdrag',
}

logger = logging.getLogger(__name__)


def get_updated_mailing_list_fields(user):
    updated_mailing_lists = []
    try:
        # Get the current user and find out what's about to change
        current_user = User.objects.get(pk=user.pk)
        if user.infomail != current_user.infomail:
            updated_mailing_lists.append('infomail')
        if user.jobmail != current_user.jobmail:
            updated_mailing_lists.append('jobmail')
    except User.DoesNotExist:
        # Find out which mailing lists are opted into if the user did not previously exist
        for mailing_list in MAILING_LIST_USER_FIELDS_TO_LIST_NAME.keys():
            if getattr(user, mailing_list, False):
                updated_mailing_lists.append(mailing_list)

    return updated_mailing_lists


@receiver(pre_save, sender=User)
def toggle_mailing_lists(sender, instance, **kwargs):
    update_fields = get_updated_mailing_list_fields(instance)

    if update_fields:
        for mailing_list in MAILING_LIST_USER_FIELDS_TO_LIST_NAME.keys():
            if mailing_list not in update_fields:
                # Skips toggle if mailing list field not changed.
                continue

            g_suite_mailing_list = MAILING_LIST_USER_FIELDS_TO_LIST_NAME[mailing_list]

            update_mailing_list.delay(
                g_suite_mailing_list,
                instance.get_email().email,
                getattr(instance, mailing_list)
            )


@receiver(signal=post_save, sender=GsuiteGroup)
def group_created_or_updated(sender, instance: GsuiteGroup, created=False, **kwargs):
    if created:
        create_gsuite_group_task.delay(group_id=instance.id)
    else:
        update_gsuite_group_task.delay(group_id=instance.id)


@receiver(signal=pre_delete, sender=GsuiteGroup)
def group_deleted(sender, instance: GsuiteGroup, **kwargs):
    delete_gsuite_group_task.delay(group_key=instance.gsuite_id)


@receiver(signal=post_save, sender=GsuiteAlias)
def alias_created_or_updated(sender, instance: GsuiteAlias, created=False, **kwargs):
    if created:
        create_gsuite_alias_task.delay(alias_id=instance.id)
    else:
        update_gsuite_alias_task.delay(alias_id=instance.id)


@receiver(signal=post_delete, sender=GsuiteAlias)
def alias_deleted(sender, instance: GsuiteAlias, **kwargs):
    delete_gsuite_alias_task.delay(group_id=instance.gsuite_group.id, alias_key=instance.email)
