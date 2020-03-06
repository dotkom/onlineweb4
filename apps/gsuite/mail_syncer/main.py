import logging
from typing import Dict, List

from django.conf import settings

from apps.authentication.models import OnlineUser as User
from apps.gsuite.mail_syncer.utils import (
    get_excess_groups_for_user,
    get_excess_users_in_g_suite,
    get_g_suite_users_for_group,
    get_missing_g_suite_group_names_for_user,
    get_missing_ow4_users_for_g_suite,
    get_ow4_users_for_group,
    insert_ow4_user_into_g_suite_group,
    remove_g_suite_user_from_group,
)

logger = logging.getLogger(__name__)


def insert_ow4_users_into_g_suite(
    domain: str,
    group_name: str,
    missing_users: List[Dict[str, str]],
    suppress_http_errors: bool = False,
):
    """
    Inserts a list of OW4 users into a G Suite group.
    :param domain: The domain in which to insert a user into a group.
    :param group_name: The name of the group to insert the user into.
    :param missing_users: A list of the missing users to be inserted into said group.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """
    for missing_user in missing_users:
        insert_ow4_user_into_g_suite_group(
            domain, group_name, missing_user, suppress_http_errors=suppress_http_errors
        )


def remove_excess_g_suite_users(
    domain: str,
    group_name: str,
    g_suite_excess_users: List[Dict[str, str]],
    suppress_http_errors: bool = False,
):
    """
    Removes excess users from a G Suite group.
    :param domain: The domain in which to remove a user from a group.
    :param group_name: The name of the group to remove the users from.
    :param g_suite_excess_users: A list of the excess users to be removed from said group.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """
    logger.info(
        "Cleaning G Suite group '{group}'.".format(group=group_name),
        extra={"group": group_name, "excess_users": g_suite_excess_users},
    )

    for excess_user in g_suite_excess_users:
        resp = remove_g_suite_user_from_group(
            domain, group_name, excess_user, suppress_http_errors=suppress_http_errors
        )
        logger.debug(f"Response from cleaning {group_name}: {resp}")


def insert_ow4_user_into_groups(
    domain: str, user: User, group_names: List[str], suppress_http_errors: bool = False
):
    """
    Inserts a single OW4 user into a G Suite group.
    :param domain: The domain in which to insert a user into a group.
    :param user: The user to update group memberships for.
    :param group_names: A list of group names to insert the user into.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """
    groups = [f"{group_name}@{domain}" for group_name in group_names]
    if groups:
        logger.info(
            f"Inserting {user} into some new G Suite groups.",
            extra={"new_groups": group_names, "user": user},
        )
    for group in groups:
        insert_ow4_user_into_g_suite_group(
            domain, group, user, suppress_http_errors=suppress_http_errors
        )


def cleanup_groups_for_user(
    domain: str, user: User, suppress_http_errors: bool = False
):
    """
    Finds excess groups for a OW4 user, and removes the user from said groups.
    :param domain: The domain in which to find a users excess group memberships.
    :param user: The user to remove excess group memberships for.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """
    excess_groups = get_excess_groups_for_user(domain, user)
    if excess_groups:
        logger.debug(
            f'Removing "{user}" from some G Suite groups.',
            extra={"user": user, "excess_groups": excess_groups},
        )
    for group in excess_groups:
        remove_g_suite_user_from_group(
            domain, group, user.online_mail, suppress_http_errors=suppress_http_errors
        )


def update_g_suite_user(
    domain: str, ow4_user: User, suppress_http_errors: bool = False
):
    """
    Finds missing and excess groups and adds and removes the user to/from them, respectively.
    :param domain: The domain in which to update a users group memberships.
    :param ow4_user: The user to update group memberships for.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """
    cleanup_groups_for_user(domain, ow4_user, suppress_http_errors=suppress_http_errors)
    insert_ow4_user_into_groups(
        domain,
        ow4_user,
        get_missing_g_suite_group_names_for_user(domain, ow4_user),
        suppress_http_errors=suppress_http_errors,
    )


def update_g_suite_group(
    domain: str, group_name: str, suppress_http_errors: bool = False
):
    """
    Finds missing and excess users and adds and removes the users to/from them, respectively.
    :param domain: The domain in which to find a group's user lists.
    :param group_name: The name of the group to get group membership status for.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    """

    if group_name.lower() not in settings.OW4_GSUITE_SYNC.get("GROUPS", {}).keys():
        logger.debug(
            f"Not running group syncer for group {group_name} - group syncing not enabled for this group"
        )
        return

    g_suite_users = get_g_suite_users_for_group(
        domain, group_name, suppress_http_errors=suppress_http_errors
    )
    ow4_users = get_ow4_users_for_group(group_name)

    excess_users = get_excess_users_in_g_suite(g_suite_users, ow4_users)
    missing_users = get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users)

    # @ToDo: Look into bulk updates
    insert_ow4_users_into_g_suite(
        domain, group_name, missing_users, suppress_http_errors=suppress_http_errors
    )
    remove_excess_g_suite_users(
        domain, group_name, excess_users, suppress_http_errors=suppress_http_errors
    )
