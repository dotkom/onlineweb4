from apps.article.models import Article
from nose.tools import assert_equal
from django_dynamic_fixture import G
import logging


def testArticleUnicodeIsCorrect():

    logger = logging.getLogger(__name__)
    logger.debug("Testing testing on Article with dynamic fixtures")

    article = G(Article)
    assert_equal(article.__unicode__(), "1")
