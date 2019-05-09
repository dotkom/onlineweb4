import logging
from unittest import mock

import requests
from django.conf import settings
from rest_framework import serializers

RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'


def validate_recaptcha(captcha_data):
    logger = logging.getLogger(__name__)
    try:
        response = requests.post(
            RECAPTCHA_URL,
            {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': captcha_data,
            }
        )
        if response.ok:
            return response.json()
        return None
    except requests.exceptions.RequestException as err:
        logger.error(err)


class RecaptchaValidator(object):

    def __call__(self, value):
        response = validate_recaptcha(value)
        success = response.get('success', False)
        errors = response.get('error-codes', [])
        if not success:
            raise serializers.ValidationError(errors)
        return None


class RecaptchaField(serializers.CharField):

    def __init__(self, write_only=True, **kwargs):
        super(RecaptchaField, self).__init__(write_only=write_only, **kwargs)
        self.validators.append(RecaptchaValidator())


def mock_validate_recaptcha():
    return mock.patch('onlineweb4.fields.recaptcha.validate_recaptcha', return_value={'success': True})
