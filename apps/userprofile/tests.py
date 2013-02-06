from apps.userprofile.models import UserProfile
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django_dynamic_fixture import G, F, N
import logging


class UserProfileTest(TestCase):
    
    def setUp(self):
        self.user=G(User, user_id=01
        self.userprofile.delete())
        #self.u1 = User.objects.create(username='user1')
        #self.up1 = UserProfile.objects.create(user=self.u1)
        #self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.userprofile=G(UserProfile, field_of_study=0, started_date=datetime.now(), user=self.user)
        self.logger=logging.getLogger(__name__)

    def tearDown(self):
        self.user.delete()
        self.userprofile.delete()

    def testIsOnline(self):
        self.logger.debug("Testing if this person is a member of online, with dynamic fixtures")
        self.assertTrue(self.userprofile.is_online())

    def testYear(self):
        self.logger.debug("Testing what year this person is, with dynamic fixtures")
        self.assertEqual(self.userprofile.years(), 1)

    def testUnicode(self):
        self.logger.debug("Testing UserProfileUnicode, with dynamic fixtures")
        self.assertEqual(self.userprofile.__unicode__(),"for %s" % self.user.username)
