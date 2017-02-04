import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from googleapiclient.errors import HttpError

from apps.authentication.models import OnlineUser as User
from apps.gsuite.auth import build_and_authenticate_g_suite_service

logger = logging.getLogger(__name__)

# Scopes for the directory API
scopes = [
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.user.alias',
]


def setup_g_suite_client():
    if not settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT'):
        logger.error('To be able to actually execute calls towards G Suite you must define DELEGATED_ACCOUNT.')
    if settings.OW4_GSUITE_SYNC.get('ENABLED') and (
            not settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT') or not settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE')):
        logger.error('To be able to execute unsafe calls towards G Suite you must allow this in settings.')
        raise ImproperlyConfigured('To actually execute unsafe calls to G Suite, allow this in OW4 settings.')

    return build_and_authenticate_g_suite_service('admin', 'directory_v1', scopes)


def get_group_key(domain, group_name):
    if not domain or not group_name:
        logger.error('You need to pass a domain and a group when generating group key.',
                     extra={'domain': domain, 'group': group_name})
        raise ValueError('You need to pass a domain and a group when generating group key.')

    email_domain = "@{domain}".format(domain=domain)
    if email_domain in group_name:
        return group_name
    return '{group}@{domain}'.format(group=group_name, domain=domain)


def get_user_key(domain, user):
    if not domain or not user:
        logger.error('You need to pass a domain and a user when generating user key.',
                     extra={'domain': domain, 'group': user})
        raise ValueError('You need to pass a domain and a user when generating user key.')

    email_domain = "@{domain}".format(domain=domain)
    if email_domain in user:
        return user
    return "{user_email}{email_domain}".format(user_email=user, email_domain=email_domain)


def get_user(original_user, gsuite=False, ow4=False):
    if not gsuite or ow4:
        raise ValueError('You need to pass either gsuite=True or ow4=True to cast user to that type.')

    gsuite_user = None
    ow4_user = None

    if isinstance(original_user, User):
        ow4_user = original_user
        gsuite_user = ow4_user.online_mail
    else:
        gsuite_user = original_user
        try:
            ow4_user = User.objects.get(online_mail__iexact=original_user)
        except User.DoesNotExist as e:
            logger.warning('User "{user}" does not exist on OW4!'.format(user=original_user))
            raise e

    return ow4_user if ow4 else gsuite_user


def insert_ow4_user_into_g_suite_group(domain, group_name, ow4_user):
    if not ow4_user.online_mail:
        logger.error("OW4 User '{user}' ({user.pk}) missing Online email address! (current: '{user.online_mail}')".
                     format(user=ow4_user),
                     extra={'user': ow4_user, 'group': group_name})
        return
        # @ToDo: This should probably trigger an error or notification, so we easily can identify this issue.
        # However, it should not stop execution of other, potentially safe, updates.

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT', False):
        logger.debug('Skipping inserting user "{user}" since ENABLE_INSERT is False.'.format(user=ow4_user))
        return

    group_key = get_group_key(domain, group_name)

    g_suite_user_dict = {
        'email': get_user_key(domain, ow4_user.online_mail),
        'role': 'MEMBER',
    }

    directory = setup_g_suite_client()

    resp = directory.members().insert(body=g_suite_user_dict, groupKey=group_key).execute()
    logger.info("Inserting '{user}' into G Suite group '{group}'.".format(user=ow4_user, group=group_key),
                extra={'user': ow4_user, 'group': group_name})
    logger.debug("Inserting response: {resp}".format(resp=resp))

    return resp


def remove_g_suite_user_from_group(domain, group_name, g_suite_user):
    if isinstance(g_suite_user, str):
        user_key = get_user_key(domain, g_suite_user)
    else:
        user_key = g_suite_user.get('email')
    if 'leder@{domain}'.format(domain=domain) == user_key or 'nestleder@{domain}'.format(domain=domain) == user_key:
        # Not removing these guys from any lists.
        logger.debug('Skipping removing user "{user}" since (s)he should be on all lists.'.format(user=user_key))
        return

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE', False):
        logger.debug('Skipping removing user "{user}" since ENABLE_DELETE is False.'.format(user=user_key))
        return

    group_key = get_group_key(domain, group_name)

    directory = setup_g_suite_client()

    resp = directory.members().delete(groupKey=group_key, memberKey=user_key).execute()
    logger.info("Removing '{user}' from G Suite group '{group}'.".format(user=user_key, group=group_key),
                 extra={'user': user_key, 'group': group_key})
    logger.debug('Removal of user response: {resp}'.format(resp=resp))

    return resp


def get_g_suite_users_for_group(domain, group_name):
    # G Suite Group Key
    group_key = get_group_key(domain, group_name)
    logger.debug("Getting G Suite member list for '{group}'.".format(group=group_key))

    directory = setup_g_suite_client()

    members = []
    try:
        members = directory.members().list(groupKey=group_key).execute().get('members')
    except HttpError as e:
        logger.error('HttpError when requesting user list: %s' % e)
        # @ToDo: Find out how to handle this properly.
        raise e

    return members


def get_g_suite_groups_for_user(domain, _user):
    user = get_user(_user, gsuite=True)

    user_key = get_user_key(domain, user)
    logger.debug("Getting G Suite user membership list for '{user}'.".format(user=user_key),
                 extra={'user': user_key})

    directory = setup_g_suite_client()

    try:
        groups = directory.groups().list(userKey=user_key).execute().get('groups')
    except HttpError as e:
        logger.error('HttpError when requesting user group membership list: %s' % e)
        # @ToDo: Find out how to handle this properly.
        raise e

    return groups


def get_ow4_users_for_group(group_name):
    return User.objects.filter(groups__name__iexact=group_name)


def get_appropriate_g_suite_group_names_for_user(domain, user):
    g_suite_groups = settings.OW4_GSUITE_SYNC.get('GROUPS')
    user_groups = user.groups.all()
    g_suite_user_groups = []
    for group in user_groups:
        if group.name.lower() in g_suite_groups.keys():
            g_suite_user_groups.append(group.name.lower())

    return g_suite_user_groups


def get_missing_g_suite_group_names_for_user(domain, user):
    user_should_be_in_groups = get_appropriate_g_suite_group_names_for_user(domain, user)
    user_is_in_groups = [g.get('name').lower() for g in get_g_suite_groups_for_user(domain, user)]

    missing_groups = []

    logger.debug('"{user}" is currently in "{in_groups}", should be in "{should_be_in_groups}".'.format(
        user=user, in_groups=user_is_in_groups, should_be_in_groups=user_should_be_in_groups),
        extra={'user': user})

    for group in user_should_be_in_groups:
        if group not in user_is_in_groups:
            missing_groups.append(group)

    return missing_groups


def get_excess_groups_for_user(domain, user):
    user_should_be_in_groups = get_appropriate_g_suite_group_names_for_user(domain, user)
    user_is_in_groups = get_g_suite_groups_for_user(domain, user)
    available_groups = settings.OW4_GSUITE_SYNC.get('GROUPS').keys()

    excess_groups = []

    for group in user_is_in_groups:
        group_name = group.get('name').lower()
        # Make sure not to remove mailing list managers from lists they have to be in.
        if group_name in available_groups and group_name not in user_should_be_in_groups:
            excess_groups.append(group.get('name'))

    return excess_groups


def check_amount_of_members_ow4_g_suite(g_suite_members, ow4_users, quiet=False):
    g_suite_count = len(g_suite_members)
    ow4_count = ow4_users.count()
    if ow4_count == g_suite_count:
        return True
    elif g_suite_count > ow4_count:
        if not quiet:
            logger.debug('There are more users in G Suite ({g_suite_count}) than on OW4 ({ow4_count}). '
                         'Need to trim inactive users from G Suite.'.format(g_suite_count=g_suite_count,
                                                                            ow4_count=ow4_count))
    else:
        if not quiet:
            logger.debug('There are more users on OW4 ({ow4_count}) than in G Suite ({g_suite_count}). '
                         'Need to update G Suite with new members.'.format(g_suite_count=g_suite_count,
                                                                            ow4_count=ow4_count))
    return False


def check_emails_match_each_other(g_suite_users, ow4_users):
    if not check_amount_of_members_ow4_g_suite(g_suite_users, ow4_users, quiet=True):
        return False

    logger.debug('Verifying that all users match to an email address.')
    for gsuite_user, ow4_user in zip(g_suite_users, ow4_users.order_by('first_name')):
        if ow4_user.online_mail != gsuite_user.get('email'):
            logger.debug("Emails do not match! '{ow4_user_email}' != '{g_suite_user_email}'".format(
                ow4_user_email=ow4_user.online_mail, g_suite_user_email=gsuite_user.get('email')))
            return False
    return True


def _get_excess_users_in_g_suite(g_suite_users, ow4_users):
    excess_users = []

    for user in g_suite_users:
        try:
            ow4_users.get(online_mail=user.get('email'))
        except User.DoesNotExist:
            excess_users.append(user)

    logger.debug('Excess users in G Suite: {excess_users}'.format(excess_users=excess_users))
    return excess_users


def _get_g_suite_user_from_g_suite_user_list(g_suite_users, g_suite_email):
    for user in g_suite_users:
        if g_suite_email == user.get('email'):
            logger.debug("Found user with G Suite email address '{g_suite_email}'".format(g_suite_email=g_suite_email))
            return user
    logger.debug("Could not find user with G Suite email address '{g_suite_email}'".format(g_suite_email=g_suite_email))
    return None


def _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users):
    missing_users = []

    for ow4_user in ow4_users:
        if not _get_g_suite_user_from_g_suite_user_list(g_suite_users, ow4_user.online_mail):
            missing_users.append(ow4_user)

    logger.debug('OW4 users missing in G Suite ({missing_users_count}): {missing_users}'.format(
        missing_users_count=len(missing_users), missing_users=missing_users))
    return missing_users
