import logging

from datetime import datetime, timedelta

from django_dynamic_fixture import G
from django.utils import timezone
from django.conf import settings
from django.test import TestCase

from apps.authentication.models import RegisterToken

class AuthenticationTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def testTokenActive(self):
        self.logger.debug("Testing that the token is active, with dynamic fixtures")
        self.registertoken=G(RegisterToken, created=timezone.now())
        self.assertTrue(self.registertoken.is_valid)

    def testTokenNotActive(self):
        self.logger.debug("Testing that the token is not active, with dynamic fixtures")
        self.registertoken=G(RegisterToken, created=timezone.now() - timedelta(days=1))
        self.assertFalse(self.registertoken.is_valid)
