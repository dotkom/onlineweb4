import logging
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.authentication.models import Email, OnlineUser, RegisterToken


class AuthenticationTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user = G(OnlineUser, username='testuser')
        self.now = timezone.now()

    def testTokenActive(self):
        self.logger.debug("Testing that the token is active, with dynamic fixtures")
        self.registertoken = G(RegisterToken, created=self.now)
        self.assertTrue(self.registertoken.is_valid)

    def testTokenNotActive(self):
        self.logger.debug("Testing that the token is not active, with dynamic fixtures")
        self.registertoken = G(RegisterToken, created=self.now - timedelta(days=1))
        self.assertFalse(self.registertoken.is_valid)

    def testYearZeroIfNoFieldOfStudy(self):
        self.user.started_date = self.now.date()
        self.assertEqual(0, self.user.year)

    def testYearOneBachelor(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 1
        self.assertEqual(1, self.user.year)

    def testYearTwoBachelor(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 1
        self.assertEqual(2, self.user.year)

    def testYearThreeBachelor(self):
        self.user.started_date = self.now.date() - timedelta(days=365*2)
        self.user.field_of_study = 1
        self.assertEqual(3, self.user.year)

    def testYearFourBachelorShouldNotBePossible(self):
        self.user.started_date = self.now.date() - timedelta(days=365*3)
        self.user.field_of_study = 1
        self.assertEqual(3, self.user.year)

    def testYearFourMaster(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 10
        self.assertEqual(4, self.user.year)

    def testYearFiveMaster(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 10
        self.assertEqual(5, self.user.year)

    def testYearSixMasterShouldNotBePossible(self):
        self.user.started_date = self.now.date() - timedelta(days=365*2)
        self.user.field_of_study = 10
        self.assertEqual(5, self.user.year)

    def testFieldOfStudy30IsAlsoMaster(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 30
        self.assertEqual(4, self.user.year)

    def testPhD(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 80
        self.assertEqual(6, self.user.year)

    def testPhdYearCouldBeInfinite(self):
        self.user.started_date = self.now.date() - timedelta(days=365*5)
        self.user.field_of_study = 80
        self.assertEqual(11, self.user.year)

    def testInternational(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 90
        self.assertEqual(1, self.user.year)

    def testInternational2(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 90
        self.assertEqual(4, self.user.year)

    def testEmailPrimaryOnCreation(self):
        email = G(Email, user=self.user, email="test@test.com")
        self.assertTrue(email.primary)
