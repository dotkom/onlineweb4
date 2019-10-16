import logging
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.offline.models import IMAGE_FOLDER, Issue
from apps.offline.tasks import create_thumbnail


def create_generic_offline_issue():
    release_date = datetime(2000, 1, 1)
    return G(Issue, release_date=release_date)


class OfflineTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.issue: Issue = G(Issue, issue=IMAGE_FOLDER + '/offline-test-pdf.pdf', image=None)

    def test_thumbnail_exists(self):
        create_thumbnail(self.issue)
        self.issue.refresh_from_db()
        self.assertTrue(self.issue.image)


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
