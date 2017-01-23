import logging

from django.conf import settings
from django.core.management.base import BaseCommand
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

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    settings.OW4_GSUITE_SYNC.get('CREDENTIALS'), scopes=scopes)
credentials = credentials.create_delegated(settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT'))

directory = build('admin', 'directory_v1', credentials=credentials)


def get_g_suite_users_for_group(domain, group_name):

    if not settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT') and (
            settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT') or settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE')):
        logger.error('To be able to actually execute calls towards G Suite you must define DELEGATED_ACCOUNT.')

    # G Suite Group Key
    group_key = "%s@%s" % (group_name.lower(), domain)
    logger.debug("Getting G Suite member list for '%s'." % group_key)

    members = []
    try:
        members = directory.members().list(groupKey=group_key).execute().get('members')
    except HttpError as e:
        logger.error('HttpError when requestion user list: %s' % e)
        # Make sure to handle this properly if this is to be used based on user interaction. It's a batch job ATM.
        raise e

    return members


def get_ow4_users_for_group(group_name):
    return User.objects.filter(groups__name__iexact=group_name)


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


def insert_ow4_user_into_g_suite(domain, group_name, ow4_user):
    if not ow4_user.online_mail:
        logger.error("OW4 User '%s' (#%i) missing Online email address! (current: '%s')"
                     % (ow4_user.get_full_name(), ow4_user.id, ow4_user.online_mail))
        return
        # @ToDo: This should probably trigger an error or notification, so we easily can identify this issue.
        # However, it should not stop execution of other, potentially safe, updates.

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_INSERT', False):
        logger.debug('Skipping inserting user %s since ENABLE_INSERT is False.' % ow4_user)
        return

    group_key = '%(group)s@%(domain)s' % {'group': group_name, 'domain': domain}

    g_suite_user_dict = {
        'email': ow4_user.online_mail,
        'role': 'MEMBER',
    }

    return directory.members().insert(body=g_suite_user_dict, groupKey=group_key).execute()


def insert_ow4_users_into_g_suite(domain, group_name, missing_users):
    for missing_user in missing_users:
        logger.debug("Inserting '%s' into G Suite group '%s'." % (missing_user, group_name))
        resp = insert_ow4_user_into_g_suite(domain, group_name, missing_user)
        logger.debug("Inserting response: %s" % resp)


def remove_g_suite_user_from_group(domain, group_name, g_suite_user):
    email = g_suite_user.get('email')
    if 'leder@%s' % domain == email or 'nestleder@%s' % domain == email:
        # Not removing these guys from any lists.
        return

    if not settings.OW4_GSUITE_SYNC.get('ENABLE_DELETE', False):
        logger.debug('Skipping removing user %s since ENABLE_DELETE is False.' % g_suite_user)
        return

    group_key = '%(group)s@%(domain)s' % {'group': group_name, 'domain': domain}

    return directory.members().delete(groupKey=group_key, memberKey=g_suite_user.get('email')).execute()


def remove_excess_g_suite_users(domain, group_name, g_suite_excess_users):
    logger.info("Cleaning G Suite group '%s' (Removing %s)" % (group_name, g_suite_excess_users))

    for excess_user in g_suite_excess_users:
        logger.debug("Removing '%s' from G Suite group '%s'." % (excess_user, group_name))
        resp = remove_g_suite_user_from_group(domain, group_name, excess_user)
        logger.debug('Removal of user response: %s' % resp)


def update_g_suite_group(domain, group_name, g_suite_users, ow4_users):
    excess_users = _get_excess_users_in_g_suite(g_suite_users, ow4_users)
    missing_users = _get_missing_ow4_users_for_g_suite(g_suite_users, ow4_users)

    # @ToDo: Look into bulk updates
    insert_ow4_users_into_g_suite(domain, group_name, missing_users)
    remove_excess_g_suite_users(domain, group_name, excess_users)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        groups_to_sync = settings.OW4_GSUITE_SYNC.get('GROUPS')
        domain = settings.OW4_GSUITE_SYNC.get('DOMAIN')

        logger.info("Starting sync of OW4 Groups' members to G Suite (domain: %s) with %s"
                    % (domain, settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT')))
        logger.debug('Groups to be synced: %s' % groups_to_sync)

        for group in groups_to_sync:
            g_suite_users = get_g_suite_users_for_group(domain, group)
            ow4_users = get_ow4_users_for_group(group)
            logger.debug('Users in OW4: %s' % ow4_users)
            logger.debug('Users in G Suite: %s' % g_suite_users)

            should_update = False
            account_count_eq = check_amount_of_members_ow4_g_suite(g_suite_users, ow4_users)
            if not account_count_eq:
                logger.debug("Updating G Suite members since the number of members are inconsistent")
                should_update = True
            else:
                logger.debug("Number of group members are equal, double checking email addresses")
                should_update = not check_emails_match_each_other(g_suite_users, ow4_users)

            if should_update:
                logger.info('Syncing %s@%s with OW4 ...' % (group, domain))
                update_g_suite_group(domain, group, g_suite_users, ow4_users)

            logger.info('%s@%s is up to date with OW4.' % (group, domain))

        logger.info('Done syncing OW4 with G Suite.')
