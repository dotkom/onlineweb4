from apps.article.models import Article
from apps.article.admin import ArticleAdmin
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from django_dynamic_fixture import G
from django.test import TestCase
import logging

class ArticleTests(TestCase):
    
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.article = G(Article, heading="test_heading")

    def testArticleUnicodeIsCorrect(self):
        self.logger.debug("Testing testing on Article with dynamic fixtures")
        self.assertEqual(self.article.__unicode__(), "test_heading")
