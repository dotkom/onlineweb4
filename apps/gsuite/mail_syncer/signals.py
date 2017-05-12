import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.gsuite.mail_syncer.utils import insert_email_into_g_suite_group
from .main import remove_g_suite_user_from_group

User = get_user_model()

MAILING_LIST_USER_FIELDS_TO_LIST_NAME = {
    'infomail': 'info',
    'jobmail': 'oppdrag',
}


@receiver(pre_save, sender=User)
def toggle_mailing_lists(sender, instance, **kwargs):
    logger = logging.getLogger(__name__)

    mailing_lists_fields = ['infomail', 'jobmail']
    update_fields = []

    current_user = User.objects.get(pk=instance.pk)
    if instance.infomail != current_user.infomail:
        update_fields.append('infomail')
    if instance.jobmail != current_user.jobmail:
        update_fields.append('jobmail')

    if update_fields:
        for mailing_list in mailing_lists_fields:
            if mailing_list not in update_fields:
                # Skips toggle if mailing list field not changed.
                continue

            domain = settings.OW4_GSUITE_SYNC.get('DOMAIN')
            g_suite_mailing_list = MAILING_LIST_USER_FIELDS_TO_LIST_NAME[mailing_list]

            if getattr(instance, mailing_list):
                insert_email_into_g_suite_group(domain, g_suite_mailing_list, instance.get_email().email)
            else:
                remove_g_suite_user_from_group(domain, g_suite_mailing_list, instance.get_email().email)


