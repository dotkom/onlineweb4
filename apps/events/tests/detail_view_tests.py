from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser

from ..models import TYPE_CHOICES, AttendanceEvent, Event, Extras, GroupRestriction
from .utils import (add_payment_delay, add_to_trikom, attend_user_to_event, generate_event,
                    generate_payment, pay_for_event)


class EventsDetailTestMixin:
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
        self.event_url = reverse(
            'events_details', args=(self.event.id, self.event.slug))


class EventsDetailRestricted(EventsDetailTestMixin, TestCase):
    def test_ok(self):
        response = self.client.get(self.event_url)

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

        response = self.client.get(self.event_url)
        messages = list(response.context['messages'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(messages), 0)

    def test_group_restricted_no_access(self):
        add_to_trikom(self.user)
        arrkom = Group.objects.get(name__iexact='arrkom')
        G(GroupRestriction, event=self.event, groups=[arrkom])

        response = self.client.get(self.event_url)
        messages = [str(message) for message in response.context['messages']]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Du har ikke tilgang til dette arrangementet.", messages)


class EventsDetailPayment(EventsDetailTestMixin, TestCase):
    def test_payment_logged_out(self):
        payment = generate_payment(self.event)

        self.client.logout()
        response = self.client.get(self.event_url)
        context = response.context

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(context['payment'], payment)
        self.assertEqual(context['user_paid'], False)
        self.assertEqual(context['payment_delay'], None)
        self.assertEqual(context['payment_relation_id'], None)

    def test_payment_not_attended(self):
        payment = generate_payment(self.event)

        response = self.client.get(self.event_url)
        context = response.context

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(context['payment'], payment)
        self.assertEqual(context['user_attending'], False)
        self.assertEqual(context['user_paid'], False)
        self.assertEqual(context['payment_delay'], None)
        self.assertEqual(context['payment_relation_id'], None)

    def test_payment_attended(self):
        payment = generate_payment(self.event)
        attend_user_to_event(self.event, self.user)

        response = self.client.get(self.event_url)
        context = response.context

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(context['payment'], payment)
        self.assertEqual(context['user_attending'], True)
        self.assertEqual(context['user_paid'], False)
        self.assertEqual(context['payment_delay'], None)
        self.assertEqual(context['payment_relation_id'], None)

    def test_payment_paid(self):
        payment = generate_payment(self.event)
        attend_user_to_event(self.event, self.user)
        payment_relation = pay_for_event(self.event, self.user)

        response = self.client.get(self.event_url)
        context = response.context

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(context['payment'], payment)
        self.assertEqual(context['user_attending'], True)
        self.assertEqual(context['user_paid'], True)
        self.assertEqual(context['payment_delay'], None)
        self.assertEqual(context['payment_relation_id'], payment_relation.id)

    def test_payment_attended_with_delay(self):
        payment = generate_payment(self.event)
        payment_delay = add_payment_delay(payment, self.user)
        attend_user_to_event(self.event, self.user)

        response = self.client.get(self.event_url)
        context = response.context

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(context['payment'], payment)
        self.assertEqual(context['user_attending'], True)
        self.assertEqual(context['user_paid'], False)
        self.assertEqual(context['payment_delay'], payment_delay)
        self.assertEqual(context['payment_relation_id'], None)


class EventsDetailExtras(EventsDetailTestMixin, TestCase):
    def extras_post(self, event_url, extras_id):
        return self.client.post(
            event_url,
            {
                'action': 'extras',
                'extras_id': extras_id
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

    def test_extras_on_non_attendance_event(self):
        event = G(Event)
        extras = G(Extras)
        event_url = reverse('events_details', args=(event.id, event.slug))

        response = self.extras_post(event_url, extras.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Dette er ikke et påmeldingsarrangement.')

    def test_extras_on_not_attended_event(self):
        extras = G(Extras)

        response = self.extras_post(self.event_url, extras.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Du er ikke påmeldt dette arrangementet.')

    def test_invalid_extras(self):
        attend_user_to_event(self.event, self.user)

        response = self.extras_post(self.event_url, 1000)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Ugyldig valg')

    def test_extras_success(self):
        extras = G(Extras)
        event = G(Event)
        G(AttendanceEvent, event=event, extras=[extras])
        attend_user_to_event(event, self.user)
        event_url = reverse(
            'events_details', args=(event.id, event.slug))

        response = self.extras_post(event_url, extras.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Lagret ditt valg')
