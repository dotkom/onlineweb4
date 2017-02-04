import logging

from apps.gsuite.mail_syncer.utils import (_get_excess_users_in_g_suite,
                                           _get_missing_ow4_users_for_g_suite,
                                           get_excess_groups_for_user,
                                           get_missing_g_suite_group_names_for_user,
                                           insert_ow4_user_into_g_suite_group,
                                           remove_g_suite_user_from_group)

logger = logging.getLogger(__name__)


def insert_ow4_users_into_g_suite(domain, group_name, missing_users):
    for missing_user in missing_users:
        insert_ow4_user_into_g_suite_group(domain, group_name, missing_user)


def remove_excess_g_suite_users(domain, group_name, g_suite_excess_users):
    logger.info("Cleaning G Suite group '{group}'.".format(group=group_name),
                extra={'group': group_name, 'excess_users': g_suite_excess_users})

    for excess_user in g_suite_excess_users:
        resp = remove_g_suite_user_from_group(domain, group_name, excess_user)
        logger.debug('Response from cleaning {group_name}: {resp}'.format(group_name=group_name, resp=resp))


def insert_ow4_user_into_groups(domain, user, group_names, suppress_http_errors=False):
    logger.info('Inserting {user} into some new G Suite groups.'.format(user=user),
                extra={'new_groups': group_names, 'user': user})
    groups = ["{group}@{domain}".format(group=group_name, domain=domain) for group_name in group_names]
    for group in groups:
        insert_ow4_user_into_g_suite_group(domain, group, user, suppress_http_errors=suppress_http_errors)


def cleanup_groups_for_user(domain, user, suppress_http_errors=False):
    excess_groups = get_excess_groups_for_user(domain, user)
    logger.debug('Removing "{user}" from some G Suite groups.'.format(user=user),
                 extra={'user': user, 'excess_groups': excess_groups})
    for group in excess_groups:
        remove_g_suite_user_from_group(domain, group, user.online_mail, suppress_http_errors=suppress_http_errors)


def update_g_suite_user(domain, ow4_user, suppress_http_errors=False):
    cleanup_groups_for_user(domain, ow4_user, suppress_http_errors=suppress_http_errors)
    insert_ow4_user_into_groups(domain, ow4_user, get_missing_g_suite_group_names_for_user(domain, ow4_user),
                                suppress_http_errors=suppress_http_errors)


def update_g_suite_group(domain, group_name, g_suite_users, ow4_users):
    excess_users = _get_excess_users_in_g_suite(g_suite_users, ow4_users)
    missing_users = _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users)

    # @ToDo: Look into bulk updates
    insert_ow4_users_into_g_suite(domain, group_name, missing_users)
    remove_excess_g_suite_users(domain, group_name, excess_users)
