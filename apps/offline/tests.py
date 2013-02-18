import logging
from os import remove
from django_dynamic_fixture import G
from django.test import TestCase
from apps.offline.models import IMAGE_FOLDER, Issue

class OfflineTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.issue = G(Issue, issue=IMAGE_FOLDER + '/offline-test-pdf.pdf')

    def testThumbnailExists(self):
        self.assertTrue(self.issue.thumbnail_exists)
        remove(self.issue.thumbnail)
