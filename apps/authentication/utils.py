import re

from unidecode import unidecode

from apps.authentication.models import OnlineUser as User


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
