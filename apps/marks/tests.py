"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from apps.marks.models import Mark
from nose.tools import assert_equal, assert_not_equal
from django_dynamic_fixture import G
import logging

def testMarks():
    logger = logging.getLogger(__name__)
    logger.debug("Testing Mark")

    mark = G(Mark)
    assert_not_equal(mark.__unicode__(), "1")
    assert_equal(mark.__unicode__(), "Prikk for 1")
   
    
    #user = G(UserEntry)
    #asser_equal(user.__unicode__(), "1")
    
