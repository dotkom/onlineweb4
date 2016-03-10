# -*- coding: utf-8 -*-

import logging

from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.approval.models import MembershipApproval
from apps.authentication.models import OnlineUser as User


class ApprovalTest(TestCase):

    def setUp(self):
        self.applicant = G(User, username="sokeren", first_name="Søker", last_name="Søkersen")
        self.approval = G(MembershipApproval, applicant=self.applicant)
        self.approval.new_expiry_date = None
        self.approval.field_of_study = 0
        self.approval.started_date = None
        self.logger = logging.getLogger(__name__)

    def testUnicodeMethod(self):
        self.logger.debug("Testing unicode output for approval")
        self.assertEqual(self.approval.__str__(), "Tom søknad for Søker Søkersen")

        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(self.approval.__str__(), "Medlemskapssøknad for Søker Søkersen")

        self.approval.field_of_study = 1
        self.approval.started_date = timezone.now().date()
        self.assertEqual(self.approval.__str__(), "Medlemskaps- og studieretningssøknad for Søker Søkersen")

        self.approval.new_expiry_date = None
        self.assertEqual(self.approval.__str__(), "studieretningssøknad for Søker Søkersen")

    def testIsMembershipApplication(self):
        self.logger.debug("Testing method to see if application is for membership")
        self.approval.field_of_study = 1
        self.assertEqual(self.approval.is_membership_application(), False)
        self.approval.started_date = timezone.now().date()
        self.assertEqual(self.approval.is_membership_application(), False)
        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.field_of_study = 0
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.started_date = None
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.new_expiry_date = None
        self.assertEqual(self.approval.is_membership_application(), False)

    def testIsFOSApplication(self):
        self.logger.debug("Testing method to see if application is for field of study update")
        self.approval.field_of_study = 1
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.started_date = timezone.now().date()
        self.assertEqual(self.approval.is_fos_application(), True)
        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(self.approval.is_fos_application(), True)
        self.approval.field_of_study = 0
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.started_date = None
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.new_expiry_date = None
        self.assertEqual(self.approval.is_fos_application(), False)
