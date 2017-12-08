import os
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import AllowedUsername, OnlineUser
from apps.payment.models import PaymentDelay

from ..models import AttendanceEvent, Event, Extras, GroupRestriction
from .utils import (add_payment_delay, add_to_trikom, attend_user_to_event, generate_event,
                    generate_payment, pay_for_event)


class EventsTestMixin:
    def setUp(self):
        G(Group, pk=1, name="arrKom")
        G(Group, pk=8, name="triKom")
        G(Group, pk=12, name="Komiteer")

        self.user = G(OnlineUser, ntnu_username='test')
        self.client.force_login(self.user)

        self.event = generate_event()
        self.event_url = reverse(
            'events_details', args=(self.event.id, self.event.slug))

    def assertInMessages(self, message_text, response):
        messages = [str(message) for message in response.context['messages']]
        self.assertIn(message_text, messages)


class EventsDetailRestricted(EventsTestMixin, TestCase):
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertInMessages(
            "Du har ikke tilgang til dette arrangementet.", response)


class EventsDetailPayment(EventsTestMixin, TestCase):
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


class EventsDetailExtras(EventsTestMixin, TestCase):
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


class EventsAttend(EventsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_attend_404(self):
        url = reverse('attend_event', args=(1000,))

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_attend_not_attendance_event(self):
        event = G(Event)
        url = reverse('attend_event', args=(event.id,))

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Dette er ikke et påmeldingsarrangement.', response)

    def test_attend_get(self):
        url = reverse('attend_event', args=(self.event.id,))

        response = self.client.get(url, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages("Vennligst fyll ut skjemaet.", response)

    def test_attend_missing_note(self):
        form_params = {'g-recaptcha-response': 'PASSED'}
        url = reverse('attend_event', args=(self.event.id,))

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages('Du må fylle inn et notat!', response)

    def test_attend_not_accepted_rules(self):
        form_params = {'g-recaptcha-response': 'PASSED'}
        url = reverse('attend_event', args=(self.event.id,))
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages('Du må godta prikkereglene!', response)

    def test_attend_invalid_captcha(self):
        url = reverse('attend_event', args=(self.event.id,))
        form_params = {'g-recaptcha-response': 'WRONG'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages(
            'Du klarte ikke captchaen! Er du en bot?', response)

    def test_attend_before_registration_start(self):
        event = G(Event)
        G(AttendanceEvent, event=event,
          registration_start=timezone.now() + timedelta(days=1),
          registration_end=timezone.now() + timedelta(days=2))
        url = reverse('attend_event', args=(event.id,))
        # django-recatpcha magic when RECAPTCHA_TESTING=True
        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Påmeldingen har ikke åpnet enda.', response)

    def test_attend_successfully(self):
        event = G(Event)
        G(
            AttendanceEvent,
            event=event,
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1)
        )
        url = reverse('attend_event', args=(event.id,))
        # django-recatpcha magic when RECAPTCHA_TESTING=True
        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du er nå meldt på arrangementet.', response)


class EventsUnattend(EventsTestMixin, TestCase):
    def test_unattend_not_attended(self):
        url = reverse('unattend_event', args=(self.event.id,))

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages(
            'Du er ikke påmeldt dette arrangementet.', response)

    def test_unattend_not_attendance_event(self):
        event = G(Event)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Dette er ikke et påmeldingsarrangement.', response)

    def test_unattend_deadline_yesterday(self):
        event = G(Event)
        G(AttendanceEvent, event=event,
          unattend_deadline=timezone.now() - timedelta(days=1))
        attend_user_to_event(event, self.user)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Avmeldingsfristen for dette arrangementet har utløpt.', response)

    def test_unattend_event_started(self):
        event = G(Event, event_start=timezone.now() - timedelta(days=1))
        G(AttendanceEvent, event=event,
          unattend_deadline=timezone.now() + timedelta(days=1))
        attend_user_to_event(event, self.user)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Dette arrangementet har allerede startet.', response)

    def test_unattend_successfully(self):
        event = G(Event, event_start=timezone.now() + timedelta(days=1))
        G(AttendanceEvent, event=event,
          unattend_deadline=timezone.now() + timedelta(days=1))
        attend_user_to_event(event, self.user)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du ble meldt av arrangementet.', response)

    def test_unattend_payment_not_refunded(self):
        event = G(Event, event_start=timezone.now() + timedelta(days=1))
        G(AttendanceEvent, event=event,
          unattend_deadline=timezone.now() + timedelta(days=1))
        attend_user_to_event(event, self.user)
        generate_payment(event)
        pay_for_event(event, self.user)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Du har betalt for arrangementet og må refundere før du kan melde deg av', response)

    def test_unattend_payment_removes_payment_delays(self):
        event = G(Event, event_start=timezone.now() + timedelta(days=1))
        G(AttendanceEvent, event=event,
          unattend_deadline=timezone.now() + timedelta(days=1))
        attend_user_to_event(event, self.user)
        payment = generate_payment(event)
        pay_for_event(event, self.user, refunded=True)
        payment_delay = add_payment_delay(payment, self.user)
        url = reverse('unattend_event', args=(event.id,))

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du ble meldt av arrangementet.', response)
        self.assertEqual(PaymentDelay.objects.filter(
            id=payment_delay.id).count(), 0)


class EventMailParticipates(EventsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.mail_url = reverse('event_mail_participants', args=(self.event.id,))

    def test_not_attendance_event(self):
        event = G(Event)
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.get(url, follow=True)

        self.assertInMessages('Dette er ikke et påmeldingsarrangement.', response)

    def test_missing_access(self):
        response = self.client.get(self.mail_url, follow=True)

        self.assertInMessages(
            'Du har ikke tilgang til å vise denne siden.', response)
