from apps.article.models import Article
from apps.article.admin import ArticleAdmin
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from django_dynamic_fixture import G
import logging
import unittest


class ArticleTests(unittest.TestCase):

    def testArticleUnicodeIsCorrect(self):

        logger = logging.getLogger(__name__)
        logger.debug("Testing testing on Article with dynamic fixtures")

        article = G(Article, heading="test_heading")
        assert_equal(article.__unicode__(), "test_heading")
