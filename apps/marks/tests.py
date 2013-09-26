import logging
from datetime import datetime, timedelta

from django_dynamic_fixture import G
from django.test import TestCase

from apps.authentication.models import OnlineUser as User
from apps.marks.models import Mark, UserEntry
from apps.marks.models import get_threshold as duration

class MarksTest(TestCase):

    def setUp(self):
        self.user=G(User)
        #Mark added 59 (working) days ago.
        markdate = duration()-timedelta(days=1)
        self.mark = G(Mark, title="1",  mark_added_date=markdate)
        self.userentry = G(UserEntry, user=self.user)
        self.logger = logging.getLogger(__name__)

    def testMarksActive(self):
        self.logger.debug("Testing if Mark is active today with dynamic fixtures")
        self.assertTrue(self.mark.is_active)
        
    def testMarkUnicode(self):    
        self.logger.debug("Testing Mark unicode with dynamic fixtures")
        self.assertEqual(self.mark.__unicode__(), "Prikk for 1")
        
    def testUserEntry(self):
        self.logger.debug("Testing UserEntry unicode with dynamic fixtures")
        self.assertEqual(self.userentry.__unicode__(), ("UserEntry for %s") % self.user.get_full_name())
