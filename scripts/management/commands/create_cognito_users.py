import re
import secrets
import string
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import boto3
import boto3.session
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.authentication.models import OnlineUser

ws = re.compile(r"\s+")

# most user phone numbers are stored as 8-digits
# some are stored with +47
# some are stored with 0047
phone_number_regex = re.compile(r"^(00|\+(?P<country_code>\d{2}))?(?P<digits>\d{8})$")


def extract_phone_number(u: OnlineUser) -> Optional[str]:
    if u.phone_number is None:
        return
    # remove whitespace
    num = ws.sub("", u.phone_number)

    m = phone_number_regex.match(num)
    if m is None:
        return

    country_code = m.group("country_code")
    if country_code is None:
        country_code = "47"
    digits = m.group("digits")

    # cognito-specific format
    return f"+{country_code}{digits}"


# this is rather ugly, but probably the least amount of code needed to give each thread its own client
thread_local = threading.local()


def setup_thread_local_cognito_client():
    # boto3 client is not thread safe, so create one per thread
    session = boto3.session.Session()
    thread_local.cognito_idp = session.client("cognito-idp")


def create_cognito_user(u: OnlineUser):
    cognito_idp = thread_local.cognito_idp

    user_attributes = [
        {
            "Name": "given_name",
            "Value": u.first_name,
        },
        {
            "Name": "family_name",
            "Value": u.last_name,
        },
        {
            "Name": "email",
            "Value": u.email,
        },
        {"Name": "gender", "Value": u.gender},
        {
            "Name": "email_verified",
            "Value": str(u.is_active),
        },
    ]

    if num := extract_phone_number(u):
        user_attributes.append(
            {
                "Name": "phone_number",
                "Value": num,
            }
        )

    cognito_user = cognito_idp.admin_create_user(
        UserPoolId=settings.COGNITO_USER_POOL_ID,
        Username=u.email,
        UserAttributes=user_attributes,
        MessageAction="SUPPRESS",
    )
    sub = cognito_user["User"]["Username"]
    u.cognito_subject = sub
    u.save()

    cognito_idp.admin_set_user_password(
        UserPoolId=settings.COGNITO_USER_POOL_ID,
        Username=sub,
        Password="".join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(20)
        ),
        Permanent=True,
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        with ThreadPoolExecutor(
            initializer=setup_thread_local_cognito_client
        ) as executor:
            for _ in executor.map(
                create_cognito_user, OnlineUser.objects.iterator(chunk_size=100)
            ):
                pass
