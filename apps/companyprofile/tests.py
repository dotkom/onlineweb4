from apps.companyprofile.models import Company
from nose.tools import assert_equal
from django_dynamic_fixture import G
import logging


def testCompanyUnicodeIsCorrect():

    logger = logging.getLogger(__name__)
    logger.debug("Testing testing on Company with dynamic fixtures")

    company = G(Company, name='lol')
    assert_equal(company.__unicode__(), "lol")
