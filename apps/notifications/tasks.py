import json
import logging

from django.conf import settings
from onlineweb4.celery import app as celery_app
from pywebpush import WebPushException, webpush

logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = settings.OW4_VAPID_PRIVATE_KEY_PATH

VAPID_CLAIMS = {
    'sub': 'mailto:dotkom@online.ntnu.no',
}


@celery_app.task(bind=True, max_retries=3)
def send_webpush(self, subscription_id, notification_id, target=None, **kwargs):
    """
    Send a webpush message asynchronously
    """
    from .models import NotificationSubscription, Notification

    subscription = NotificationSubscription.objects.get(id=subscription_id)
    notification = Notification.objects.get(id=notification_id)

    """ Convert subscription info to VAPID format """
    subscription_info = {
        'endpoint': subscription.endpoint,
        'keys': {
            'auth': subscription.auth,
            'p256dh': subscription.p256dh,
        }
    }

    data = json.dumps(notification.data)

    try:
        webpush(
            subscription_info=subscription_info,
            data=data,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
        notification.sent = True
        notification.save()
    except WebPushException as error:
        logger.error(error)
        # Mozilla returns additional information in the body of the response.
        if error.response and error.response.json():
            logger.error(error.response.json())
    except TypeError as error:
        logger.error(error)
        raise error
