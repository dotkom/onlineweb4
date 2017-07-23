from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from apps.events.tests import create_generic_event
from django_dynamic_fixture import G
from apps.authentication.models import OnlineUser as User
from django.contrib.auth.models import Group, Permission


def add_permissions(user):
    user.groups.add(G(Group, name='Komiteer'))
    user.user_permissions.add(
        Permission.objects.filter(codename='view_event').first(),
        Permission.objects.filter(codename='add_event').first()
    )


class DashboardEventsURLTestCase(TestCase):
    def setUp(self):
        self.user = G(User)
        self.client.force_login(self.user)

    def test_dashboard_events_index_missing_permissions(self):
        url = reverse('dashboard_events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_events_index_empty(self):
        add_permissions(self.user)
        url = reverse('dashboard_events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_index_exists(self):
        create_generic_event()
        add_permissions(self.user)
        url = reverse('dashboard_events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_events_create(self):
        add_permissions(self.user)
        url = reverse('dashboard_event_create')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_events_details(self):
        add_permissions(self.user)
        event = create_generic_event()
        url = reverse('dashboard_event_details', kwargs={'event_id': event.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_events_edit(self):
        add_permissions(self.user)
        event = create_generic_event()
        url = reverse('dashboard_events_edit', kwargs={'event_id': event.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
