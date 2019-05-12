import logging

from pywebpush import webpush, WebPushException

from onlineweb4.celery import app as celery_app
from apps.notifications.models import NotificationSubscription


logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = ''
VAPID_CLAIMS = {
    'sub': 'mailto:dotkom@online.ntnu.no'
}

@celery_app.task(bind=True, max_retries=3)
def send_webpush(self, subscription: NotificationSubscription, target=None, **kwargs):
    """
    Send a webpush message asynchronously
    """

    """ Convert subscription info to VAPID format """
    subscription_info = {
        'endpoint': subscription.endpoint,
        'keys': {
            'auth': subscription.auth,
            'p256dh': subscription.p256dh,
        }
    }

    data = kwargs.get('data')

    try:
        webpush(
            subscription_info=subscription_info,
            data=data,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
    except WebPushException as error:
        logger.error(error)
        # Mozilla returns additional information in the body of the response.
        if error.response and error.response.json():
            logger.error(error.response.json())
