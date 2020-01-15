import json
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from googleapiclient.errors import HttpError
from onlineweb4.celery import app

from apps.gsuite import models
from apps.gsuite.mail_syncer.utils import insert_email_into_g_suite_group

from .main import remove_g_suite_user_from_group
from .utils import (
    add_alias_to_gsuite_group,
    create_or_sync_gsuite_group,
    delete_alias_from_gsuite_group,
    delete_gsuite_group,
    update_alias,
    update_gsuite_group,
)

User = get_user_model()


def _get_error_message_from_httperror(err: HttpError) -> str:
    """
    Parses an HTTP Error from the Google API and returns the error message.
    :param err: An error from the Google API.
    :return: The error message.
    """
    json_error = json.loads(str(err.content.decode()))
    return json_error.get("error", {}).get("message", "")


def insert_user_into_group_pass_if_already_member(domain: str, group: str, email: str):
    """
    Subscribes an email address to a mailing list. If the email address is already subscribed, silently pass.
    :param domain: The G Suite domain in question.
    :param group: The group to add an email to.
    :param email: The email address to add to the group.
    :return: Nothing. Raises exception if failed.
    """
    logger = logging.getLogger(__name__)

    try:
        insert_email_into_g_suite_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if "Member already exists" in error_message:
            logger.warning(
                f'Email address "{email}" was already subscribed to mailing list "{group}"!'
            )
        else:
            raise err


def remove_user_from_group_pass_if_not_subscribed(domain: str, group: str, email: str):
    """
    Unsubscribes an email address from a mailing list. If the email address is not already subscribed, silently pass.
    :param domain: The G Suite domain in question.
    :param group: The group to add an email to.
    :param email: The email address to add to the group.
    :return: Nothing. Raises exception if failed.
    """
    logger = logging.getLogger(__name__)

    try:
        remove_g_suite_user_from_group(domain, group, email)
    except HttpError as err:
        error_message = _get_error_message_from_httperror(err)

        if "Resource Not Found" in error_message:
            logger.warning(
                f'Email address "{email}" was not subscribed to mailing list "{group}"!'
            )
        else:
            raise err


@shared_task
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


@app.task(bind=True)
def create_gsuite_group_task(self, group_id: int):
    group = models.GsuiteGroup.objects.get(pk=group_id)
    create_or_sync_gsuite_group(group)


@app.task(bind=True)
def update_gsuite_group_task(self, group_id: int):
    group = models.GsuiteGroup.objects.get(pk=group_id)
    update_gsuite_group(group)


@app.task(bind=True)
def delete_gsuite_group_task(self, group_key: str):
    delete_gsuite_group(group_key)


@app.task(bind=True)
def create_gsuite_alias_task(self, alias_id: int):
    alias = models.GsuiteAlias.objects.get(pk=alias_id)
    add_alias_to_gsuite_group(alias)


@app.task(bind=True)
def update_gsuite_alias_task(self, alias_id: int):
    alias = models.GsuiteAlias.objects.get(pk=alias_id)
    update_alias(alias)


@app.task(bind=True)
def delete_gsuite_alias_task(self, group_id: int, alias_key: str):
    group = models.GsuiteGroup.objects.get(pk=group_id)
    delete_alias_from_gsuite_group(group, alias_key)
