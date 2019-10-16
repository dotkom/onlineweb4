# -*- encoding: utf-8 -*-

import logging

from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.companyprofile.models import Company
from apps.online_oidc_provider.test import OIDCTestCase


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


class CompanyAPITestCase(OIDCTestCase):

    def setUp(self):
        self.url = reverse('companies-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.company: Company = G(Company, name='online')

    def test_company_api_returns_200_ok(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_can_get_company_by_id(self):
        response = self.client.get(self.id_url(self.company.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('name'), self.company.name)

    def test_client_can_filter_companies_by_name(self):
        other_company: Company = G(Company, name='evilcorp')

        response = self.client.get(f'{self.url}?name={self.company.name}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        company_names = list(map(lambda company: company.get('name'), response.json().get('results')))

        self.assertIn(self.company.name, company_names)
        self.assertNotIn(other_company.name, company_names)
