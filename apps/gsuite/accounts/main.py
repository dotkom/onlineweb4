import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from googleapiclient.errors import HttpError

from apps.authentication.utils import create_online_mail_alias
from apps.gsuite.accounts.utils import create_temporary_password, setup_g_suite_client
from apps.gsuite.utils import get_user_key

logger = logging.getLogger(__name__)


def create_g_suite_account(ow4_user):

    if not ow4_user.online_mail:
        create_online_mail_alias(ow4_user)

    directory = setup_g_suite_client()

    password = create_temporary_password()

    query = directory.users().insert(body={
        "primaryEmail": "{}@{}".format(ow4_user.online_mail, settings.OW4_GSUITE_SETTINGS.get('DOMAIN')),
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
