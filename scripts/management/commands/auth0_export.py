import json
import re
from base64 import b64encode
from typing import Optional
from uuid import uuid4

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

    return f"+{country_code}{digits}"


def create_auth0_user(u: OnlineUser):
    if not u.has_usable_password:
        print(f"Skipping {u}, no usable password")
        return None
    if u.email is None or len(u.email) == 0:
        print(f"Skipping {u}, no email")
        return None
    # if u.auth0_subject is not None:
    #     print(f"Skipping {u}, already migrated")
    #     return None

    try:
        algorithm, iterations, salt, hash = u.password.split("$", 3)
    except ValueError as e:
        print(f"{e=}\n{u=}\n{u.password=}")
        return None

    # thank you https://community.auth0.com/t/wrong-password-for-imported-users-from-django/61105
    salt = b64encode(salt.encode()).decode().replace("=", "")
    hash = hash.replace("=", "")
    iterations = int(iterations)
    # we probably only use pbkdf2_sha256, in auth0 they use -
    algorithm = algorithm.replace("_", "-")

    id = str(uuid4())
    u.auth0_subject = f"auth0|{id}"
    u.save()

    auth0_user = {
        "user_id": id,
        "email": u.email,
        "email_verified": u.is_active,
        "given_name": u.first_name,
        "family_name": u.last_name,
        "name": f"{u.first_name} {u.last_name}",
        "custom_password_hash": {
            "algorithm": "pbkdf2",
            "hash": {
                "encoding": "utf-8",
                "value": f"$pbkdf2-sha256$i={iterations},l=32${salt}${hash}",
            },
        },
    }

    if len(u.first_name) == 0:
        del auth0_user["given_name"]

    if len(u.last_name) == 0:
        del auth0_user["family_name"]

    if num := extract_phone_number(u):
        auth0_user["mfa_factors"] = [{"phone": {"value": num}}]

    return auth0_user


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = [
            create_auth0_user(u) for u in OnlineUser.objects.iterator(chunk_size=100)
        ]
        users = [u for u in users if u is not None]
        N = 700
        for i in range(3):
            file = json.dumps(users[i * N : i * N + N])
            with open(f"auth0_users{i}.json", "w") as f:
                f.write(file)
