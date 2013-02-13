from apps.companyprofile.models import Company
from django_dynamic_fixture import G
from django.test import TestCase

import logging

class CompanyTests(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.company = G(Company, name="testname") 


    def testCompanyUniqodeIsCorrect(self):
        self.logger.debug("Company __unicode__() should return correct name")
        self.assertEqual(self.company.__unicode__(), "testname")    
