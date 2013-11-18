from datetime import datetime, time, timedelta
import logging

from django_dynamic_fixture import G
from django.utils import timezone
from django.test import TestCase

from apps.authentication.models import OnlineUser as User
from apps.marks.models import Mark, UserEntry
from apps.marks.models import _get_expiration_date

class MarksTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user=G(User)
        self.mark = G(Mark, title="Testprikk", added_date=timezone.now())
        self.userentry = G(UserEntry, user=self.user)

    def testMarksActive(self):
        self.logger.debug("Testing if Mark is active")
        self.assertTrue(self.mark.is_active)
        
    def testMarkUnicode(self):    
        self.logger.debug("Testing Mark unicode with dynamic fixtures")
        self.assertEqual(unicode(self.mark), u"Prikk for Testprikk")
        
    def testUserEntry(self):
        self.logger.debug("Testing UserEntry unicode with dynamic fixtures")
        self.assertEqual(unicode(self.userentry), ("UserEntry for %s") % self.user.get_full_name())

    def testGettingExpirationDateWithNoVacationInSpring(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        date = timezone.make_aware(datetime.combine(datetime(2013, 2, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2013, 4, 2), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWithSummerVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        date = timezone.make_aware(datetime.combine(datetime(2013, 5, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2013, 9, 13), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWithNoVacationInFall(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        date = timezone.make_aware(datetime.combine(datetime(2013, 9, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2013, 10, 31), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWithWinterVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        date = timezone.make_aware(datetime.combine(datetime(2013, 11, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2014, 2, 14), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWhenDateBetweenNewYearsAndEndOfWinterVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        date = timezone.make_aware(datetime.combine(datetime(2013, 1, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2013, 3, 16), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWhenDateBetweenStartOfWinterVacationAndNewYears(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        date = timezone.make_aware(datetime.combine(datetime(2013, 12, 15), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2014, 3, 16), time()), timezone.get_current_timezone()), prikk.expiration_date)

    def testGettingExpirationDateWhenDateInSummerVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        date = timezone.make_aware(datetime.combine(datetime(2013, 7, 1), time()), timezone.get_current_timezone())
        prikk = G(Mark, added_date=date)
        self.assertEqual(timezone.make_aware(datetime.combine(datetime(2013, 10, 14), time()), timezone.get_current_timezone()), prikk.expiration_date)
