"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from unittest import skip

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class ResourceCenterURLTestCase(TestCase):
    def test_resourcecenter_index(self):
        url = reverse('resourcecenter_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resourcecenter_gameservers(self):
        url = reverse('resourcecenter_gameservers')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
