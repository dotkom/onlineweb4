# -*- encoding: utf-8 -*-

import logging

from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.companyprofile.models import Company


class CompanyTests(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.company = G(Company, name="testname")

    def testCompanyUniqodeIsCorrect(self):
        self.logger.debug("Company __str__() should return correct name")
        self.assertEqual(self.company.__str__(), "testname")


class CompanyProfileURLTestCase(TestCase):
    def test_company_profile_detail(self):
        company = G(Company)

        url = reverse('company_details', args=(company.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
