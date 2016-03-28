from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status

from apps.splash.models import SplashYear


class SplashURLTestCase(TestCase):
    def test_splash_index_no_events(self):
        url = reverse('splash_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_splash_index_exist(self):
        G(SplashYear)
        url = reverse('splash_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_splash_calendar(self):
        url = reverse('splash_calendar')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
