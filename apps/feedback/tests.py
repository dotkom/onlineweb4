"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _


class SimpleTest(TestCase):
    fixtures = ["test_feedback_fixture.json"]

    def test_post_correct(self):
        #TODO: do eeet! test posted against db (Sigurd) 2013-02-08
        pass

#    def test_post_incorrect(self):
#        resp = self.client.post("/feedback/auth/user/1/1/")
#        self.assertEqual(resp.status_code, 200)
#        for i in range(len(resp.context['answers'])):
#            self.assertIn(unicode(_(u'This field is required.')),
#                          resp.context['answers'][i].errors['answer'])
#    
#    def test_good_urls(self):
#        resp = self.client.get("/feedback/auth/user/1/1/")
#        self.assertEqual(resp.status_code, 200)
#
#        resp = self.client.get("/feedback/auth/user/1/1/results")
#        self.assertEqual(resp.status_code, 200)
#
#    def test_bad_urls(self):
#        resp = self.client.get("/feedback/auth/user/100/1/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/user/1/100/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/user/100/100/")
#        self.assertEqual(resp.status_code, 404)
#
#        resp = self.client.get("/feedback/auth/derp/1/1/")
#        self.assertEqual(resp.status_code, 404)
