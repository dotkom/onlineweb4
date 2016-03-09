import logging
from os import remove
from subprocess import CalledProcessError, check_call

from apps.offline.models import IMAGE_FOLDER, Issue
from django.test import TestCase
from django_dynamic_fixture import G


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
