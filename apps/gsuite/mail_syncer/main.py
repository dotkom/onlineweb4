import logging

from apps.gsuite.mail_syncer.utils import (_get_excess_users_in_g_suite,
                                           _get_missing_ow4_users_for_g_suite,
                                           get_excess_groups_for_user,
                                           get_missing_g_suite_group_names_for_user,
                                           insert_ow4_user_into_g_suite_group,
                                           remove_g_suite_user_from_group)

logger = logging.getLogger(__name__)


def insert_ow4_users_into_g_suite(domain, group_name, missing_users):
    """
    Inserts a list of OW4 users into a G Suite group.
    :param domain: The domain in which to insert a user into a group.
    :type domain: str
    :param group_name: The name of the group to insert the user into.
    :type group_name: str
    :param missing_users: A list of the missing users to be inserted into said group.
    :type missing_users: list
    """
    for missing_user in missing_users:
        insert_ow4_user_into_g_suite_group(domain, group_name, missing_user)


def remove_excess_g_suite_users(domain, group_name, g_suite_excess_users):
    """
    Removes excess users from a G Suite group.
    :param domain: The domain in which to remove a user from a group.
    :type domain: str
    :param group_name: The name of the group to remove the users from.
    :type group_name: str
    :param g_suite_excess_users: A list of the excess users to be removed from said group.
    :type g_suite_excess_users: list
    """
    logger.info("Cleaning G Suite group '{group}'.".format(group=group_name),
                extra={'group': group_name, 'excess_users': g_suite_excess_users})

    for excess_user in g_suite_excess_users:
        resp = remove_g_suite_user_from_group(domain, group_name, excess_user)
        logger.debug('Response from cleaning {group_name}: {resp}'.format(group_name=group_name, resp=resp))


def insert_ow4_user_into_groups(domain, user, group_names, suppress_http_errors=False):
    """
    Inserts a single OW4 user into a G Suite group.
    :param domain: The domain in which to insert a user into a group.
    :type domain: str
    :param user: The user to update group memberships for.
    :type user: apps.authentication.models.OnlineUser
    :param group_names: A list of group names to insert the user into.
    :type group_names: list
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :type suppress_http_errors: bool
    """
    logger.info('Inserting {user} into some new G Suite groups.'.format(user=user),
                extra={'new_groups': group_names, 'user': user})
    groups = ["{group}@{domain}".format(group=group_name, domain=domain) for group_name in group_names]
    for group in groups:
        insert_ow4_user_into_g_suite_group(domain, group, user, suppress_http_errors=suppress_http_errors)


def cleanup_groups_for_user(domain, user, suppress_http_errors=False):
    """
    Finds excess groups for a OW4 user, and removes the user from said groups.
    :param domain: The domain in which to find a users excess group memberships.
    :type domain: str
    :param user: The user to remove excess group memberships for.
    :type user: apps.authentication.models.OnlineUser
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :type suppress_http_errors: bool
    """
    excess_groups = get_excess_groups_for_user(domain, user)
    logger.debug('Removing "{user}" from some G Suite groups.'.format(user=user),
                 extra={'user': user, 'excess_groups': excess_groups})
    for group in excess_groups:
        remove_g_suite_user_from_group(domain, group, user.online_mail, suppress_http_errors=suppress_http_errors)


def update_g_suite_user(domain, ow4_user, suppress_http_errors=False):
    """
    Finds missing and excess groups and adds and removes the user to/from them, respectively.
    :param domain: The domain in which to update a users group memberships.
    :type domain: str
    :param ow4_user: The user to update group memberships for.
    :type ow4_user: apps.authentication.models.OnlineUser
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :type suppress_http_errors: bool
    """
    cleanup_groups_for_user(domain, ow4_user, suppress_http_errors=suppress_http_errors)
    insert_ow4_user_into_groups(domain, ow4_user, get_missing_g_suite_group_names_for_user(domain, ow4_user),
                                suppress_http_errors=suppress_http_errors)


def update_g_suite_group(domain, group_name, g_suite_users, ow4_users):
    """
    Finds missing and excess users and adds and removes the users to/from them, respectively.
    :param domain: The domain in which to find a group's user lists.
    :type domain: str
    :param group_name: The name of the group to get group membership status for.
    :type group_name: str
    :param g_suite_users: A list of G Suite users to update group memberships for.
    :type g_suite_users: list
    :param ow4_users: A list of OW4 users to update group memberships for.
    :type ow4_users: list
    """
    excess_users = _get_excess_users_in_g_suite(g_suite_users, ow4_users)
    missing_users = _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users)

    # @ToDo: Look into bulk updates
    insert_ow4_users_into_g_suite(domain, group_name, missing_users)
    remove_excess_g_suite_users(domain, group_name, excess_users)
