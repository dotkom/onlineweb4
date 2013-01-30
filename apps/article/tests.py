from apps.article.models import Article
from django_dynamic_fixture import G

import logging
import unittest


class ArticleTests(unittest.TestCase):

    def testArticleUnicodeIsCorrect(self):

        logger = logging.getLogger(__name__)
        logger.debug("Testing testing on Article with dynamic fixtures")

        article = G(Article, heading="test_heading")
        self.assertEqual(article.__unicode__(), "test_heading")
