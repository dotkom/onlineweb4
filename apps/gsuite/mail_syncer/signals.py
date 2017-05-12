import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from googleapiclient.errors import HttpError

from apps.gsuite.mail_syncer.utils import insert_email_into_g_suite_group
from .main import remove_g_suite_user_from_group

User = get_user_model()

MAILING_LIST_USER_FIELDS_TO_LIST_NAME = {
    'infomail': 'info',
    'jobmail': 'oppdrag',
}


def _get_error_message_from_httperror(err):
    """
    Parses an HTTP Error from the Google API and returns the error message.
    :param err: An error from the Google API.
    :type err: HttpError
    :return: The error message.
    :rtype: str
    """
    json_error = json.loads(str(err.content.decode()))
    logging.debug('HttpErr %s' % json_error)
    return json_error.get('error', {}).get('message', '')


def insert_user_into_group_pass_if_already_member(domain, group, email):
    """
    Subscribes an email address to a mailing list. If the email address is already subscribed, silently pass.
    :param domain: The G Suite domain in question.
    :type domain: str
    :param group: The group to add an email to.
    :type group: str
    :param email: The email address to add to the group.
    :type email: str
    :return: Nothing. Raises exception if failed.
    :rtype None
    """
    logger = logging.getLogger(__name__)

    try:
        insert_email_into_g_suite_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if 'Member already exists' in error_message:
            logger.warning('Email address "{email}" was already subscribed to mailing list "{list}"!'.format(
                email=email, list=group
            ))
        else:
            raise err


def remove_user_from_group_pass_if_not_subscribed(domain, group, email):
    """
    Unsubscribes an email address from a mailing list. If the email address is not already subscribed, silently pass.
    :param domain: The G Suite domain in question.
    :type domain: str
    :param group: The group to add an email to.
    :type group: str
    :param email: The email address to add to the group.
    :type email: str
    :return: Nothing. Raises exception if failed.
    :rtype None
    """
    logger = logging.getLogger(__name__)

    try:
        remove_g_suite_user_from_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if 'Resource Not Found' in error_message:
            logger.warning('Email address "{email}" was not subscribed to mailing list "{list}"!'.format(
                email=email, list=group
            ))
        else:
            raise err


@receiver(pre_save, sender=User)
def toggle_mailing_lists(sender, instance, **kwargs):

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
                insert_user_into_group_pass_if_already_member(domain, g_suite_mailing_list, instance.get_email().email)
            else:
                remove_user_from_group_pass_if_not_subscribed(domain, g_suite_mailing_list, instance.get_email().email)
