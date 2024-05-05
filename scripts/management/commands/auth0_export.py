import json
import re
from base64 import b64encode
from uuid import uuid4

from django.core.management.base import BaseCommand

from apps.authentication.models import Email, OnlineUser

ws = re.compile(r"\s+")

# most user phone numbers are stored as 8-digits
# some are stored with +47
# some are stored with 0047
phone_number_regex = re.compile(r"^(00|\+(?P<country_code>\d{2}))?(?P<digits>\d{8})$")


def extract_phone_number(u: OnlineUser) -> str | None:
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
        print(f"Skipping {u.pk}, no usable password")
        return None
    if u.email is None or len(u.email) == 0:
        emails = Email.objects.filter(user=u)
        # print(u.email_user)
        print(f"Skipping {u.pk}, no email or? {emails}")
        return None
    # if u.auth0_subject is not None:
    #     print(f"Skipping {u}, already migrated")
    #     return None

    try:
        algorithm, iterations, salt, hash = u.password.split("$", 3)
    except ValueError as e:
        print(f"{e}\n{u.pk=}\n{u.password=}")
        return None

    # thank you https://community.auth0.com/t/wrong-password-for-imported-users-from-django/61105
    salt = b64encode(salt.encode()).decode().replace("=", "")
    hash = hash.replace("=", "")
    iterations = int(iterations)
    # we probably only use pbkdf2_sha256, in auth0 they use -
    algorithm = algorithm.replace("_", "-")

    user_previously_exported = True
    if not u.auth0_subject:
        user_previously_exported = False
        id = str(uuid4())
        u.auth0_subject = f"auth0|{id}"

    auth0_user = {
        "user_id": u.auth0_subject.split("|")[1],
        "email": u.email,
        "email_verified": u.is_active,
        "given_name": u.first_name,
        "family_name": u.last_name,
        "user_metadata": {},
        "app_metadata": {
            "ow4_userid": u.pk,
        },
    }

    if not user_previously_exported:
        # we do not want to export passwords of existing users in auth0
        # auth0 then just errors out, and users might not remember their passwords
        auth0_user["custom_password_hash"] = {
            "algorithm": "pbkdf2",
            "hash": {
                "encoding": "utf-8",
                "value": f"$pbkdf2-sha256$i={iterations},l=32${salt}${hash}",
            },
        }

    if len(u.first_name) == 0:
        del auth0_user["given_name"]

    if len(u.last_name) == 0:
        del auth0_user["family_name"]

    if num := extract_phone_number(u):
        auth0_user["user_metadata"]["phone"] = num

    if len(auth0_user["user_metadata"]) == 0:
        del auth0_user["user_metadata"]

    return (u, auth0_user)


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = OnlineUser.objects.filter(is_active=True)
        users = [create_auth0_user(u) for u in qs.iterator(chunk_size=100)]
        users = [u for u in users if u is not None]
        N = 700
        for i in range(int(qs.count() / N) + 1):
            chunk = users[i * N : i * N + N]
            OnlineUser.objects.bulk_update([u for (u, _) in chunk], ["auth0_subject"])
            file = json.dumps([a0u for (_, a0u) in chunk])
            with open(f"auth0_users_prod_{i}.json", "w") as f:
                f.write(file)
