from .utils import generate_event
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status


class EventsURLTestCase(TestCase):
    def test_ok(self):
        event = generate_event()

        url = reverse('events_details', args=(event.id, event.slug))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
