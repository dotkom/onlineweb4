import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.splash.models import SplashEvent


class SplashModelsTestCase(TestCase):
    def test_str_equals_title(self):
        event = G(SplashEvent)

        self.assertEqual(event.title, event.__str__())


class SplashURLTestCase(APITestCase):
    def test_calendar_export(self):
        G(SplashEvent)
        url = reverse('splash_calendar')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SplashAPIURLTestCase(APITestCase):
    def test_splash_events_list_no_events(self):
        url = reverse('splashevent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_splash_events_list_with_events_exist(self):
        G(SplashEvent)
        url = reverse('splashevent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_splash_events_list_filter_future(self):
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        next_week = datetime.datetime.now() + datetime.timedelta(days=7)

        G(SplashEvent, start_time=last_week, end_time=last_week)
        next_week_event = G(SplashEvent, start_time=next_week, end_time=next_week)

        url = reverse('splashevent-list')

        url += '?start_time__gte=%s' % datetime.datetime.now()

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data.get('count'))
        self.assertEqual(next_week_event.title, response.data.get('results')[0].get('title'))
