# encoding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class AutoConfigTest(TestCase):

    def setUp(self):
        self.request_factory = Client()
        self.valid_address = 'foo@online.ntnu.no'

    def test_http_response_is_200_on_valid_email(self):
        response = self.request_factory.get('/mail/config-v1.1.xml', {'emailaddress': self.valid_address})
        self.assertEqual(response.status_code, 200)

    def test_http_bad_request(self):
        response = self.request_factory.get('/mail/config-v1.1.xml', {'emailaddress': 'not.online@ntnu.no'})
        self.assertEqual(response.status_code, 400)
