import logging

from django.conf import settings

from apps.gsuite.mail_syncer.utils import (
    get_missing_g_suite_group_names_for_user, get_excess_groups_for_user, _get_excess_users_in_g_suite,
    _get_missing_ow4_users_for_g_suite, insert_ow4_user_into_g_suite_group, remove_g_suite_user_from_group
)


logger = logging.getLogger(__name__)


def insert_ow4_users_into_g_suite(domain, group_name, missing_users):
    for missing_user in missing_users:
        insert_ow4_user_into_g_suite_group(domain, group_name, missing_user)


def remove_excess_g_suite_users(domain, group_name, g_suite_excess_users):
    logger.info("Cleaning G Suite group '%s' (Removing %s)" % (group_name, g_suite_excess_users))

    for excess_user in g_suite_excess_users:
        resp = remove_g_suite_user_from_group(domain, group_name, excess_user)


def insert_ow4_user_into_groups(domain, user, group_names):
    logger.debug('Inserting %s into new G Suite groups (%s)' % (user, group_names))
    groups = ["%s@online.ntnu.no" % group_name for group_name in group_names]
    for group in groups:
        insert_ow4_user_into_g_suite_group(domain, group, user)


def cleanup_groups_for_user(domain, user):
    excess_groups = get_excess_groups_for_user(domain, user)
    logger.debug('Removing %s from some G Suite groups (%s)' % (user, excess_groups))
    for group in excess_groups:
        remove_g_suite_user_from_group(domain, group, user.online_mail)


def update_g_suite_user(domain, ow4_user):
    cleanup_groups_for_user(domain, ow4_user)
    insert_ow4_user_into_groups(domain, ow4_user, get_missing_g_suite_group_names_for_user(domain, ow4_user))


def update_g_suite_group(domain, group_name, g_suite_users, ow4_users):
    excess_users = _get_excess_users_in_g_suite(g_suite_users, ow4_users)
    missing_users = _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users)

    # @ToDo: Look into bulk updates
    insert_ow4_users_into_g_suite(domain, group_name, missing_users)
    remove_excess_g_suite_users(domain, group_name, excess_users)
