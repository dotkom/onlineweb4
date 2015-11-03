from datetime import date
import logging

from django_dynamic_fixture import G
from django.utils import timezone
from django.test import TestCase

from apps.authentication.models import OnlineUser as User
from apps.marks.models import Mark, MarkUser
from apps.marks.models import _get_with_duration_and_vacation


class MarksTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user = G(User)
        self.mark = G(Mark, title="Testprikk", added_date=timezone.now().date())
        self.userentry = G(MarkUser, user=self.user, mark=self.mark)

# Rewrite to check
#    def testMarksActive(self):
#        self.logger.debug("Testing if Mark is active")
#        self.assertTrue(self.mark.is_active)

    def testMarkUnicode(self):
        self.logger.debug("Testing Mark unicode with dynamic fixtures")
        self.assertEqual(str(self.mark), u"Prikk for Testprikk")

    def testMarkUser(self):
        self.logger.debug("Testing MarkUser unicode with dynamic fixtures")
        self.assertEqual(str(self.userentry), "Mark entry for user: %s" % self.user.get_full_name())

    def testGettingExpirationDateWithNoVacationInSpring(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 2, 1)
        self.assertEqual(date(2013, 3, 3), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithSummerVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        d = date(2013, 5, 15)
        self.assertEqual(date(2013, 8, 28), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithNoVacationInFall(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 9, 1)
        self.assertEqual(date(2013, 10, 1), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithWinterVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        d = date(2013, 11, 15)
        self.assertEqual(date(2014, 1, 29), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateBetweenNewYearsAndEndOfWinterVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 1, 1)
        self.assertEqual(date(2013, 2, 14), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateBetweenStartOfWinterVacationAndNewYears(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 12, 15)
        self.assertEqual(date(2014, 2, 14), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateInSummerVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 7, 1)
        self.assertEqual(date(2013, 9, 14), _get_with_duration_and_vacation(d))
