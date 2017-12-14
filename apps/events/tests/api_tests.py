from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .utils import generate_event


class EventsAPIURLTestCase(APITestCase):
    def test_events_list_empty(self):
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_list_exists(self):
        generate_event()
        url = reverse('events-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):
        event = generate_event()
        url = reverse('events-detail', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
