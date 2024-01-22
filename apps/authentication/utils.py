import logging
import re
import uuid
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.loader import render_to_string
from rest_framework.request import Request
from rest_framework.reverse import reverse
from unidecode import unidecode

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import RegisterToken


def create_online_mail_alias(user: User) -> str:
    proposal = unidecode(user.get_full_name()).lower()
    # exchange whitespace with dots
    proposal = re.sub(r"\s+", ".", proposal)
    # remove everything but lowercase letters and dots
    proposal = re.sub(r"[^a-z.]", "", proposal)

    final_proposal = proposal
    edition = 2
    # guard against duplicates
    while User.objects.filter(online_mail=final_proposal).count() > 0:
        final_proposal = f"{proposal}{edition}"
        edition += 1

    return final_proposal


def send_register_verification_email(user: User, email_obj: Email, request: Request):
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
