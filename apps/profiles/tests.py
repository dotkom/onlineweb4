"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User


class ProfilesURLTestCase(TestCase):
    def test_user_search(self):
        user = G(User)
        url = reverse('profiles_user_search')

        self.client.force_login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
