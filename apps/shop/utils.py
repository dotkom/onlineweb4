from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users

from .models import MagicToken


def send_magic_link(user, token):
    rfid_confirm_link = reverse("shop_set_rfid", args=[str(token.token)])

    message = render_to_string(
        "shop/email/magic_link.txt",
        {
            "user": token.user,
            "rfid_confirm_link": "{}{}".format(settings.BASE_URL, rfid_confirm_link),
        },
    )
    send_message_to_users(
        title="Oppdatert RFID på online.ntnu.no",
        content=message,
        recipients=[user],
        permission_type=PermissionType.DEFAULT,
        url=rfid_confirm_link,
    )

    return token


def create_magic_token(user, rfid, send_token_by_email=False):
    token = MagicToken.objects.create(user=user, data=rfid)

    if send_token_by_email:
        send_magic_link(user, token)
    return token
