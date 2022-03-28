import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from googleapiclient.errors import HttpError

try:
    from zappa.asynchronous import task
except ImportError:
    # Zappa is only required if we are running on Lambda
    def task(func):
        return func


from apps.gsuite.mail_syncer.utils import insert_email_into_g_suite_group

from .main import remove_g_suite_user_from_group

User = get_user_model()


def _get_error_message_from_httperror(err: HttpError) -> str:
    """
    Parses an HTTP Error from the Google API and returns the error message.
    """
    json_error = json.loads(str(err.content.decode()))
    return json_error.get("error", {}).get("message", "")


def insert_user_into_group_pass_if_already_member(
    domain: str, group: str, email: str
) -> None:
    """
    Subscribes an email address to a mailing list.
    If the email address is already subscribed, silently pass.
    Raises exception if failed.
    """
    logger = logging.getLogger(__name__)

    try:
        insert_email_into_g_suite_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if "Member already exists" in error_message:
            logger.warning(
                'Email address "{email}" was already subscribed to mailing list "{list}"!'.format(
                    email=email, list=group
                )
            )
        else:
            raise err


def remove_user_from_group_pass_if_not_subscribed(
    domain: str, group: str, email: str
) -> None:
    """
    Unsubscribes an email address from a mailing list.
    If the email address is not already subscribed, silently pass.
    Raises exception if failed.
    """
    logger = logging.getLogger(__name__)

    try:
        remove_g_suite_user_from_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if "Resource Not Found" in error_message:
            logger.warning(
                'Email address "{email}" was not subscribed to mailing list "{list}"!'.format(
                    email=email, list=group
                )
            )
        else:
            raise err


@task
def update_mailing_list(g_suite_mailing_list, email, added):
    domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")
    if added:
        insert_user_into_group_pass_if_already_member(
            domain, g_suite_mailing_list, email
        )
    else:
        remove_user_from_group_pass_if_not_subscribed(
            domain, g_suite_mailing_list, email
        )
