from .utils import generate_event, add_to_trikom
from ..models import GroupRestriction, TYPE_CHOICES
from apps.authentication.models import OnlineUser
from django.contrib.auth.models import Group
from django.test import TestCase

from django.core.urlresolvers import reverse
from rest_framework import status
from django_dynamic_fixture import G


class EventsURLTestCase(TestCase):
    def setUp(self):
        G(Group, pk=1, name="arrKom")
        G(Group, pk=3, name="bedKom")
        G(Group, pk=6, name="fagKom")
        G(Group, pk=5, name="eksKom")
        G(Group, pk=8, name="triKom")
        G(Group, pk=12, name="Komiteer")

        self.user = G(OnlineUser)
        self.client.force_login(self.user)

        self.event = generate_event(TYPE_CHOICES[0][0])

    def test_ok(self):
        url = reverse('events_details', args=(self.event.id, self.event.slug))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_404(self):
        event = generate_event()
        url = reverse('events_details', args=(event.id + 10, event.slug))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_restricted_access(self):
        add_to_trikom(self.user)
        trikom = Group.objects.get(name__iexact='trikom')
        G(GroupRestriction, event=self.event, groups=[trikom])
        url = reverse('events_details', args=(self.event.id, self.event.slug))

        response = self.client.get(url)
        messages = list(response.context['messages'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(messages), 0)

    def test_group_restricted_no_access(self):
        add_to_trikom(self.user)
        arrkom = Group.objects.get(name__iexact='arrkom')
        G(GroupRestriction, event=self.event, groups=[arrkom])
        url = reverse('events_details', args=(self.event.id, self.event.slug))

        response = self.client.get(url)
        messages = [str(message) for message in response.context['messages']]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Du har ikke tilgang til dette arrangementet.", messages)
