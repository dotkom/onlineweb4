from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from .models import MagicToken


def send_magic_link(user, rfid):
    token = MagicToken.objects.create(user=user, data=rfid)

    rfid_confirm_link = reverse('shop_set_rfid', args=[str(token.token)])

    message = render_to_string('shop/email/magic_link.txt', {
        'user': token.user,
        'rfid_confirm_link': '{}{}'.format(settings.BASE_URL, rfid_confirm_link),
    })
    send_mail('Oppdatert RFID på online.ntnu.no', message, settings.DEFAULT_FROM_EMAIL, [user.get_email().email])
