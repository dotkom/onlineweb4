import logging
from datetime import datetime
from os import remove
from subprocess import CalledProcessError, check_call

from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.offline.models import IMAGE_FOLDER, Issue


def create_generic_offline_issue():
    release_date = datetime(2000, 1, 1)
    return G(Issue, release_date=release_date)


class OfflineTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.issue = G(Issue, issue=IMAGE_FOLDER + '/offline-test-pdf.pdf')

    def _runImagemagick(self):
        try:
            check_call(['which', 'convert'])
            return True
        except (OSError, CalledProcessError):
            self.logger.error('Missing dependency imagemagick.')
            return False

    def testImagemagickExists(self):
        self.assertTrue(self._runImagemagick())

    def testThumbnailExists(self):
        self.assertTrue(self.issue.thumbnail_exists)

    def tearDown(self):
        remove(self.issue.thumbnail)


class OfflineURLTestCase(TestCase):
    def test_offline_index_empty(self):
        url = reverse('offline')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offline_index_exists(self):
        create_generic_offline_issue()

        url = reverse('offline')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfflineAPIURLTestCase(APITestCase):
    def test_offline_list_empty(self):
        url = reverse('issue-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offline_list_exists(self):
        create_generic_offline_issue()

        url = reverse('issue-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offline_detail(self):
        issue = create_generic_offline_issue()
        url = reverse('issue-detail', args=(issue.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
