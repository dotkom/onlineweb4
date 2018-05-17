import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .tasks import update_mailing_list

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
