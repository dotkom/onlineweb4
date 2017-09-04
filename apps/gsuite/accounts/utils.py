import logging
import uuid

from django.conf import settings
from googleapiclient.errors import HttpError

from apps.gsuite.auth import build_and_authenticate_g_suite_service
from apps.gsuite.utils import get_user_key

logger = logging.getLogger(__name__)

# Scopes for the directory API
scopes = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.user.alias',
]


def setup_g_suite_client():
    """
    Sets up a working API client towards the Google Developers API.
    Requires various Django settings to be set to function properly.
    :return: Google API Client
    :rtype: googleapiclient.discovery.Resource
    """
    if not settings.OW4_GSUITE_ACCOUNTS.get('ENABLED', False):
        logger.debug('Trying to setup G Suite API client, but OW4_GSUITE_ACCOUNTS is not enabled.')
        return
    if not settings.OW4_GSUITE_SETTINGS.get('DELEGATED_ACCOUNT'):
        logger.error('To be able to actually execute calls towards G Suite you must define DELEGATED_ACCOUNT.')
    if settings.OW4_GSUITE_ACCOUNTS.get('ENABLED') and not settings.OW4_GSUITE_ACCOUNTS.get('ENABLE_INSERT'):
        logger.warning('To be able to execute unsafe calls towards G Suite you must allow this in settings.'
                       '"ENABLE_INSERT" is not enabled.')

    return build_and_authenticate_g_suite_service('admin', 'directory_v1', scopes)


def create_temporary_password():
    return str(uuid.uuid4())[:8]


def user_exists_in_g_suite(ow4_user):
    if not ow4_user.online_mail:
        return False

    directory = setup_g_suite_client()

    q = directory.users().get(userKey=get_user_key(settings.OW4_GSUITE_SETTINGS.get('DOMAIN'), ow4_user.online_mail))

    try:
        q.execute()
        return True
    except HttpError as err:
        logger.debug('G Suite account not found for {}. Err: {}'.format(ow4_user, err))
        if err.resp.status == 404:
            return False
