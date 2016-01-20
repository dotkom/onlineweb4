import logging

from django_dynamic_fixture import G
from django.test import TestCase

from apps.article.models import Article


class ArticleTests(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.article = G(Article, heading="test_heading")

    def testArticleUnicodeIsCorrect(self):
        self.logger.debug("Article __str__() should return correct heading")
        self.assertEqual(self.article.__str__(), "test_heading")
