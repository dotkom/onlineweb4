import logging
from unittest import mock

import requests
from django.conf import settings
from rest_framework import serializers

TURNSTILE_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def validate_turnstile(captcha_data):
    logger = logging.getLogger(__name__)
    try:
        response = requests.post(
            TURNSTILE_URL,
            {"secret": settings.TURNSTILE_SECRET, "response": captcha_data},
        )
        if response.ok:
            return response.json()
        return None
    except requests.exceptions.RequestException as err:
        logger.error(err)


class TurnstileValidator:
    def __call__(self, value):
        response = validate_turnstile(value)
        success = response.get("success", False)
        errors = response.get("error-codes", [])
        if not success:
            raise serializers.ValidationError(errors)
        return None


class TurnstileField(serializers.CharField):
    def __init__(self, write_only=True, **kwargs):
        super().__init__(write_only=write_only, **kwargs)
        self.validators.append(TurnstileValidator())


def mock_validate_turnstile():
    return mock.patch(
        "onlineweb4.fields.turnstile.validate_turnstile", return_value={"success": True}
    )
