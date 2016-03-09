# -*- encoding: utf-8 -*-

import logging

from apps.companyprofile.models import Company
from django.test import TestCase
from django_dynamic_fixture import G


class CompanyTests(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.company = G(Company, name="testname")

    def testCompanyUniqodeIsCorrect(self):
        self.logger.debug("Company __str__() should return correct name")
        self.assertEqual(self.company.__str__(), "testname")
