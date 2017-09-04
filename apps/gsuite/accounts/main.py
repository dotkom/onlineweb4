import logging
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from googleapiclient.errors import HttpError

from apps.authentication.utils import create_online_mail_alias
from apps.gsuite.auth import build_and_authenticate_g_suite_service
from apps.gsuite.mail_syncer.main import update_g_suite_user
from apps.gsuite.mail_syncer.utils import get_user_key

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


def create_g_suite_account(ow4_user):

    if not ow4_user.online_mail:
        create_online_mail_alias(ow4_user)

    directory = setup_g_suite_client()

    password = create_temporary_password()

    domain = settings.OW4_GSUITE_SETTINGS.get('DOMAIN')

    query = directory.users().insert(body={
        "primaryEmail": "{}@{}".format(ow4_user.online_mail, domain),
        "password": password,
        "name": {
            "givenName": ow4_user.first_name,
            "familyName": ow4_user.last_name,
            "fullName": ow4_user.get_full_name(),
        },
        "changePasswordAtNextLogin": True
    })

    try:
        resp = query.execute()
    except HttpError as err:
        logger.error('HttpError while requesting G Suite Account creation: {}'.format(err.content),
                     extra={"error": err})
        if err.resp.status == 409:
            logger.error('G Suite account creation: User "{}@online.ntnu.no" already exists.'
                         .format(ow4_user.online_mail))
        raise err

    logger.info('Created G Suite account for "{user}" with username "{gsuite_username}"'.format(
        user=ow4_user, gsuite_username=resp.get('primaryEmail')))
    logger.debug('Created G Suite account, response: {}'.format(resp))

    notify_g_suite_user_account(ow4_user, password)

    update_g_suite_user(domain, ow4_user)

    return resp


def reset_password_g_suite_account(ow4_user):
    if not ow4_user.online_mail:
        raise ValueError('Det finnes ingen G Suite konto for denne epostadressen.')

    directory = setup_g_suite_client()

    password = create_temporary_password()

    user_key = get_user_key(settings.OW4_GSUITE_SETTINGS.get('DOMAIN'), ow4_user.online_mail)

    logger.debug('Resetting G Suite password for {}.'.format(ow4_user))

    resp = directory.users().update(body={
        "password": password,
        "changePasswordAtNextLogin": True,
    }, userKey=user_key)  # .execute()

    logger.debug('Reset G Suite password for {}, resp: {}'.format(ow4_user, resp))

    notify_g_suite_user_account(ow4_user, password)


def notify_g_suite_user_account(user, password):
    logger.debug('Notifying user about new G Suite account')
    message = render_to_string('authentication/email/gsuite_account_notification.txt', {
        "user": user,
        "password": password,
    })
    send_mail('Informasjon om G Suite konto fra Online', message, settings.EMAIL_DOTKOM, [user.get_email().email])
