import re

from django.core.exceptions import ValidationError


def validate_rfid(rfid):
    if not re.match(r"^\d{8,10}$", rfid):
        raise ValidationError("Dette er ikke en gyldig RFID.")
