import logging
import re
import uuid
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Q
from django.template.loader import render_to_string
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from unidecode import unidecode

from apps.authentication.models import Email, OnlineUser, RegisterToken


def create_online_mail_alias(user):
    logger = logging.getLogger(__name__)
    email_username = unidecode(user.get_full_name()).lower().replace(" ", ".")

    if user.online_mail:
        logger.info(
            'Trying to create online mail address for {user} who already has the address "{address}".'.format(
                user=user, address=email_username
            )
        )

    if OnlineUser.objects.filter(online_mail=email_username).count() > 0:
        logger.error(
            'Creating G Suite mail address for "{user}" failed since address "{address}" already exists.'.format(
                user=user.get_full_name(), address=email_username
            )
        )
        raise ValueError(
            "Adressen er allerede i bruk. Ta kontakt med dotkom for å fikse problemet."
        )

    user.online_mail = email_username
    user.save()


def create_online_mail_aliases():
    # We only sync in members of the Komiteer group
    group = Group.objects.get(name="Komiteer")
    # Fetch all users that do not currently have an alias
    nomail = group.user_set.filter(
        Q(online_mail__isnull=True) | Q(online_mail__exact="")
    ).order_by("id")
    # Find a list of all taken email aliases in the system already
    online_mails = OnlineUser.objects.filter(online_mail__isnull=False).exclude(
        online_mail__exact=""
    )
    taken_mails = [u.online_mail for u in online_mails]

    for user in nomail:
        # Decode the full name of the user to plain ascii
        name = unidecode(user.get_full_name()).lower()

        # Users which lack mail or a name are not considered
        if not name or not user.email:
            continue

        # set to empty string so nothing is appended if not needed
        i = ""
        while True:
            # Start with a suggestion that is only lower case name replaced spaces with dots
            suggestion = re.sub(r"\s+", ".", name)
            # Suggestion now contains only lowercase letters, dots and possibly other chars
            # Like dashes. The following regex is a catch-all and removes them.
            suggestion = re.sub(r"[^a-z.]", "", suggestion)
            # Append the differentiation number
            suggestion += str(i)
            if suggestion not in taken_mails:
                user.online_mail = suggestion
                user.save()
                break
            # If the alias already exists, append a number, starting with 2
            else:
                i = i + 1 if i else 2

    # Then produce a list of "alias: email" for all users in Komiteer
    for user in group.user_set.all():
        if user.online_mail and user.email:
            print("%s: %s" % (user.online_mail, user.email))


def send_register_verification_email(
    user: OnlineUser, email_obj: Email, request: Request
) -> Response:
    logger = logging.getLogger(__name__)

    token = uuid.uuid4().hex

    try:
        RegisterToken.objects.create(user=user, email=email_obj.email, token=token)
        logger.info(f"Successfully registered token for {user}")
    except IntegrityError as error:
        logger.error(f"Failed to register token for {user} due to {error}")

    verify_url = reverse("auth_verify", args=[token], request=request)
    message = render_to_string("auth/email/welcome_tpl.txt", {"verify_url": verify_url})

    try:
        send_mail(
            "Verifiser din konto",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email_obj.email],
        )
        logger.info(f"Account verification email sent to {user} via {email_obj.email}")
    except SMTPException as error:
        logging.error(f"Failed to send verification email to {user} due to {error}")
