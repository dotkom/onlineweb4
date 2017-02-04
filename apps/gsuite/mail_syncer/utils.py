import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from apps.authentication.models import OnlineUser as User

logger = logging.getLogger(__name__)

scopes = [
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.user.alias',
]

credentials = None
if settings.OW4_GSUITE_SYNC.get('ENABLED'):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        settings.OW4_GSUITE_SYNC.get('CREDENTIALS'), scopes=scopes)
    credentials = credentials.create_delegated(settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT'))

directory = build('admin', 'directory_v1', credentials=credentials)


def _check_setup_ok():
    if not settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT'):
        logger.error('To be able to actually execute calls towards G Suite you must define DELEGATED_ACCOUNT.')
    if settings.OW4_GSUITE_SYNC.get('ENABLED') and (
            not settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT') or not settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE')):
        logger.error('To be able to execute unsafe calls towards G Suite you must allow this in settings.')
        raise ImproperlyConfigured('To actually execute unsafe calls to G Suite, allow this in OW4 settings.')
    return True


def get_group_key(domain, group_name):
    if not domain or not group_name:
        raise ValueError('You need to pass a domain and a user when generating user key.')

    email_domain = "@%s" % domain
    if email_domain in group_name:
        return group_name
    return '%(group)s@%(domain)s' % {'group': group_name, 'domain': domain}


def get_user_key(domain, user):
    if not domain or not user:
        raise ValueError('You need to pass a domain and a user when generating user key.')

    email_domain = "@%s" % domain
    if email_domain in user:
        return user
    return "%s%s" % (user, email_domain)


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
            logger.warning('User "%s" does not exist on OW4!' % original_user)
            raise e

    return ow4_user if ow4 else gsuite_user


def insert_ow4_user_into_g_suite_group(domain, group_name, ow4_user):
    if not ow4_user.online_mail:
        logger.error("OW4 User '%s' (#%i) missing Online email address! (current: '%s')"
                     % (ow4_user.get_full_name(), ow4_user.id, ow4_user.online_mail))
        return
        # @ToDo: This should probably trigger an error or notification, so we easily can identify this issue.
        # However, it should not stop execution of other, potentially safe, updates.

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT', False):
        logger.debug('Skipping inserting user %s since ENABLE_INSERT is False.' % ow4_user)
        return

    group_key = get_group_key(domain, group_name)

    g_suite_user_dict = {
        'email': get_user_key(domain, ow4_user.online_mail),
        'role': 'MEMBER',
    }

    logger.info("Inserting '%s' into G Suite group '%s'." % (ow4_user.online_mail, group_key))
    resp = directory.members().insert(body=g_suite_user_dict, groupKey=group_key).execute()
    logger.debug("Inserting response: %s" % resp)

    return resp


def remove_g_suite_user_from_group(domain, group_name, g_suite_user):
    if isinstance(g_suite_user, str):
        user_key = get_user_key(domain, g_suite_user)
    else:
        user_key = g_suite_user.get('email')
    if 'leder@%s' % domain == user_key or 'nestleder@%s' % domain == user_key:
        # Not removing these guys from any lists.
        return

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE', False):
        logger.debug('Skipping removing user %s since ENABLE_DELETE is False.' % g_suite_user)
        return

    group_key = get_group_key(domain, group_name)

    logger.debug("Removing '%s' from G Suite group '%s'." % (user_key, group_key))
    resp = directory.members().delete(groupKey=group_key, memberKey=user_key).execute()
    logger.debug('Removal of user response: %s' % resp)

    return resp


def get_g_suite_users_for_group(domain, group_name):
    if not _check_setup_ok():
        return []

    # G Suite Group Key
    group_key = get_group_key(domain, group_name)
    logger.debug("Getting G Suite member list for '%s'." % group_key)

    members = []
    try:
        members = directory.members().list(groupKey=group_key).execute().get('members')
    except HttpError as e:
        logger.error('HttpError when requesting user list: %s' % e)
        # @ToDo: Find out how to handle this properly.
        raise e

    return members


def get_g_suite_groups_for_user(domain, _user):
    if not _check_setup_ok():
        return []

    user = get_user(_user, gsuite=True)

    user_key = get_user_key(domain, user)
    logger.debug("Getting G Suite user membership list for '%s'." % user_key)

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

    logger.debug('"%s" is currently in "%s", should be in "%s".' % (user, user_should_be_in_groups, user_is_in_groups))

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
            logger.debug('There are more users in G Suite (%i) than on OW4 (%i). '
                         'Need to trim inactive users from G Suite.' % (g_suite_count, ow4_count))
    else:
        if not quiet:
            logger.debug('There are more users on OW4 (%i) than in G Suite (%i). '
                         'Need to update G Suite with new members.' % (ow4_count, g_suite_count))
    return False


def check_emails_match_each_other(g_suite_users, ow4_users):
    if not check_amount_of_members_ow4_g_suite(g_suite_users, ow4_users, quiet=True):
        return False

    logger.debug('Verifying that all users match to an email address.')
    for gsuite_user, ow4_user in zip(g_suite_users, ow4_users.order_by('first_name')):
        if ow4_user.online_mail != gsuite_user.get('email'):
            logger.warning("Emails do not match! '%s' != '%s'" % (ow4_user.online_mail, gsuite_user.get('email')))
            return False
    return True


def _get_excess_users_in_g_suite(g_suite_users, ow4_users):
    excess_users = []

    for user in g_suite_users:
        try:
            ow4_users.get(online_mail=user.get('email'))
        except User.DoesNotExist:
            excess_users.append(user)

    logger.debug('Excess users in G Suite: %s' % excess_users)
    return excess_users


def _get_g_suite_user_from_g_suite_user_list(g_suite_users, g_suite_email):
    for user in g_suite_users:
        if g_suite_email == user.get('email'):
            logger.debug("Found user with G Suite email address '%s'" % g_suite_email)
            return user
    logger.debug("Could not find user with G Suite email address '%s'" % g_suite_email)
    return None


def _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users):
    missing_users = []

    for ow4_user in ow4_users:
        if not _get_g_suite_user_from_g_suite_user_list(g_suite_users, ow4_user.online_mail):
            missing_users.append(ow4_user)

    logger.debug('OW4 users missing in G Suite(%i): %s' % (len(missing_users), missing_users))
    return missing_users
