from datetime import timedelta
from unittest.mock import patch

from captcha.client import RecaptchaResponse
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from freezegun import freeze_time
from rest_framework import status

from apps.authentication.models import AllowedUsername
from apps.payment.models import PaymentDelay, PaymentPrice

from ..models import TYPE_CHOICES, AttendanceEvent, Event, Extras, GroupRestriction, Registration
from .utils import (add_payment_delay, add_to_arrkom, add_to_bedkom, add_to_trikom,
                    attend_user_to_event, generate_attendee, generate_event, generate_payment,
                    generate_registration, generate_user, pay_for_event)


def get_attend_url(event_id: int, registration_id: int):
    return reverse('attend_event', args=[event_id, registration_id])


def get_unattend_url(event_id: int):
    return reverse('unattend_event', args=[event_id])


class EventsTestMixin:
    def setUp(self):
        G(Group, pk=1, name="arrKom")
        G(Group, pk=3, name="bedKom")
        G(Group, pk=8, name="triKom")
        G(Group, pk=12, name="Komiteer")

        self.user = generate_user('test')
        self.client.force_login(self.user)

        self.event = generate_event()
        self.registration = generate_registration(attendance=self.event.attendance_event)
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

    def test_group_hidden_no_access(self):
        self.event = G(Event, visible=False)
        self.event_url = reverse(
            'events_details', args=(self.event.id, self.event.slug))

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
        attend_user_to_event(self.event, self.user, self.registration)

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
        attend_user_to_event(self.event, self.user, self.registration)
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
        attend_user_to_event(self.event, self.user, self.registration)

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
        attend_user_to_event(self.event, self.user, self.registration)

        response = self.extras_post(self.event_url, 1000)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Ugyldig valg')

    def test_extras_success(self):
        extras = G(Extras)
        event = G(Event)
        G(AttendanceEvent, event=event, extras=[extras])
        attend_user_to_event(event, self.user, self.registration)
        event_url = reverse(
            'events_details', args=(event.id, event.slug))

        response = self.extras_post(event_url, extras.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'],
                         'Lagret ditt valg')


class EventsAttend(EventsTestMixin, TestCase):

    def test_attend_404(self):
        url = get_attend_url(1000, 2000)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_attend_not_attendance_event(self):
        event = G(Event)
        url = get_attend_url(event.id, self.registration.id)

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Dette er ikke et påmeldingsarrangement.', response)

    def test_attend_get(self):
        url = get_attend_url(self.event.id, self.registration.id)

        response = self.client.get(url, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages("Vennligst fyll ut skjemaet.", response)

    def test_attend_missing_note(self):
        form_params = {'g-recaptcha-response': 'PASSED'}
        url = get_attend_url(self.event.id, self.registration.id)

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages('Du må fylle inn et notat!', response)

    def test_attend_not_accepted_rules(self):
        form_params = {'g-recaptcha-response': 'PASSED'}
        url = get_attend_url(self.event.id, self.registration.id)
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages('Du må godta prikkereglene!', response)

    @patch("captcha.fields.client.submit")
    def test_attend_invalid_captcha(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=False)
        url = get_attend_url(self.event.id, self.registration.id)
        form_params = {'g-recaptcha-response': 'WRONG'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages(
            'Du klarte ikke captchaen! Er du en bot?', response)

    @patch("captcha.fields.client.submit")
    def test_attend_before_registration_start(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        event = G(Event)
        attendance_event: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            registration_start=timezone.now() + timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=2)
        )
        registration: Registration = G(Registration, attendance=attendance_event)

        url = get_attend_url(event.id, registration.id)

        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Påmeldingen har ikke åpnet enda.', response)

    @patch("captcha.fields.client.submit")
    def test_attend_successfully(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        event: Event = G(Event)
        attendance_event: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1)
        )
        registration: Registration = G(Registration, attendance=attendance_event)

        url = get_attend_url(event.id, registration.id)

        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du er nå meldt på arrangementet.', response)

    @patch("captcha.fields.client.submit")
    def test_attend_twice(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        event: Event = G(Event)
        attendance_event: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1)
        )
        registration: Registration = G(Registration, attendance=attendance_event)

        url = get_attend_url(event.id, registration.id)

        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        self.client.post(url, form_params, follow=True)
        response = self.client.post(url, form_params, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Du er allerede meldt på dette arrangementet.', response)

    @patch("captcha.fields.client.submit")
    def test_attend_with_payment_creates_paymentdelay(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        event: Event = G(Event)
        attendance_event: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1)
        )
        registration: Registration = G(Registration, attendance=attendance_event)

        self.event_payment = generate_payment(event, payment_type=3, delay=timedelta(days=2))
        G(PaymentPrice, price=200, payment=self.event_payment)
        url = get_attend_url(event.id, registration.id)

        form_params = {'g-recaptcha-response': 'PASSED'}
        G(AllowedUsername, username=self.user.ntnu_username,
          expiration_date=timezone.now() + timedelta(days=1))
        self.user.mark_rules = True
        self.user.save()

        self.client.post(url, form_params, follow=True)

        self.assertTrue(PaymentDelay.objects.filter(user=self.user).exists())


class EventsUnattend(EventsTestMixin, TestCase):
    def test_unattend_not_attended(self):
        url = get_unattend_url(self.event.id)

        response = self.client.post(url, follow=True)

        self.assertRedirects(response, self.event.get_absolute_url())
        self.assertInMessages(
            'Du er ikke påmeldt dette arrangementet.', response)

    def test_unattend_deadline_yesterday(self):
        event: Event = G(Event)
        attendance: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            unattend_deadline=timezone.now() - timedelta(days=1),
        )
        registration: Registration = G(Registration, attendance=attendance)
        attend_user_to_event(event, self.user, registration)

        url = get_unattend_url(event.id)
        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Avmeldingsfristen for dette arrangementet har utløpt.', response)

    def test_unattend_event_started(self):
        event: Event = G(Event, event_start=timezone.now() - timedelta(days=1))
        attendance: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            unattend_deadline=timezone.now() + timedelta(days=1),
        )
        registration: Registration = G(Registration, attendance=attendance)
        attend_user_to_event(event, self.user, registration)

        url = get_unattend_url(event.id)
        response = self.client.post(url, follow=True)

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Dette arrangementet har allerede startet.', response)

    def test_unattend_successfully(self):
        event: Event = G(Event, event_start=timezone.now() + timedelta(days=1))
        attendance: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            unattend_deadline=timezone.now() + timedelta(days=1),
        )
        registration: Registration = G(Registration, attendance=attendance)
        attend_user_to_event(event, self.user, registration)

        url = get_unattend_url(event.id)

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du ble meldt av arrangementet.', response)

    def test_unattend_payment_not_refunded(self):
        event: Event = G(Event, event_start=timezone.now() + timedelta(days=1))
        attendance: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            unattend_deadline=timezone.now() + timedelta(days=1)
        )
        registration: Registration = G(Registration, attendance=attendance)
        attend_user_to_event(event, self.user, registration)
        generate_payment(event)
        pay_for_event(event, self.user)

        url = get_unattend_url(event.id)

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages(
            'Du har betalt for arrangementet og må refundere før du kan melde deg av', response)

    def test_unattend_payment_removes_payment_delays(self):
        event: Event = G(Event, event_start=timezone.now() + timedelta(days=1))
        attendance: AttendanceEvent = G(
            AttendanceEvent,
            event=event,
            unattend_deadline=timezone.now() + timedelta(days=1),
        )
        registration: Registration = G(Registration, attendance=attendance)
        attend_user_to_event(event, self.user, registration)
        payment = generate_payment(event)
        pay_for_event(event, self.user, refunded=True)
        payment_delay = add_payment_delay(payment, self.user)

        url = get_unattend_url(event.id)

        response = self.client.post(url, follow=True, HTTP_HOST='example.com')

        self.assertRedirects(response, event.get_absolute_url())
        self.assertInMessages('Du ble meldt av arrangementet.', response)
        self.assertEqual(PaymentDelay.objects.filter(
            id=payment_delay.id).count(), 0)


class EventsUnattendWaitlist(TestCase):
    def setUp(self):
        self.event = G(Event, event_start=timezone.now() + timedelta(days=1))
        G(AttendanceEvent, event=self.event,
          unattend_deadline=timezone.now() + timedelta(days=1), waitlist=True)
        self.registration = G(Registration, attendance=self.event.attendance_event, max_capacity=2)

        self.user = generate_user('test')
        self.client.force_login(self.user)
        self.other_user = generate_user('other')
        self.url = get_unattend_url(self.event.id)

    def test_unattend_notifies_waitlist_when_attending(self):
        generate_attendee(self.event, 'user1', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        generate_attendee(self.event, 'user2', self.registration)
        generate_attendee(self.event, 'user3', self.registration)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Du har fått plass på', mail.outbox[0].subject)

    def test_unattend_does_not_notify_waitlist_when_on_waitlist(self):
        generate_attendee(self.event, 'user1', self.registration)
        generate_attendee(self.event, 'user2', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        generate_attendee(self.event, 'user3', self.registration)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2017-01-01 12:00")
    def test_payment_type_instant_uses_extended(self):
        generate_payment(self.event, payment_type=1)
        generate_attendee(self.event, 'user1', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        attend_user_to_event(self.event, self.other_user, self.registration)
        generate_attendee(self.event, 'user3', self.registration)
        payment_delay_time = timedelta(days=2)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Du har fått plass på', mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)

    def test_payment_delay_is_not_created_if_deadline_over_48_hours(self):
        generate_payment(self.event, payment_type=2, deadline=timezone.now() + timedelta(days=3))
        generate_attendee(self.event, 'user1', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        attend_user_to_event(self.event, self.other_user, self.registration)
        generate_attendee(self.event, 'user3', self.registration)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Du har fått plass på', mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.filter(user=self.other_user)
        self.assertFalse(payment_delay.exists())

    @freeze_time("2017-01-01 12:00")
    def test_payment_delay_is_created_if_deadline_under_48_hours(self):
        generate_payment(self.event, payment_type=2, deadline=timezone.now() + timedelta(hours=47))
        generate_attendee(self.event, 'user1', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        attend_user_to_event(self.event, self.other_user, self.registration)
        generate_attendee(self.event, 'user3', self.registration)
        payment_delay_time = timedelta(days=2)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Du har fått plass på', mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)

    @freeze_time("2017-01-01 12:00")
    def test_payment_type_delay_uses_payment_delay(self):
        delay_days = 4
        payment_delay_time = timedelta(days=delay_days)
        generate_payment(self.event, payment_type=3, delay=payment_delay_time)
        generate_attendee(self.event, 'user1', self.registration)
        attend_user_to_event(self.event, self.user, self.registration)
        attend_user_to_event(self.event, self.other_user, self.registration)
        generate_attendee(self.event, 'user3', self.registration)

        self.client.post(self.url, follow=True, HTTP_HOST='example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Du har fått plass på', mail.outbox[0].subject)
        payment_delay = PaymentDelay.objects.get(user=self.other_user)
        self.assertEqual(payment_delay.valid_to, timezone.now() + payment_delay_time)


class EventMailParticipates(EventsTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.mail_url = reverse(
            'event_mail_participants', args=(self.event.id,))

    def test_not_attendance_event(self):
        event = G(Event)
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.get(url, follow=True)

        self.assertInMessages(
            'Dette er ikke et påmeldingsarrangement.', response)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_access(self):
        response = self.client.get(self.mail_url, follow=True)

        self.assertInMessages(
            'Du har ikke tilgang til å vise denne siden.', response)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_own_social_event_as_bedkom(self):
        add_to_bedkom(self.user)
        bedkom = Group.objects.get(name__iexact='bedkom')
        event = generate_event(TYPE_CHOICES[0][0], organizer=bedkom)
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.context['event'], event)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_as_arrkom(self):
        add_to_arrkom(self.user)
        event = generate_event(TYPE_CHOICES[0][0])
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.context['event'], event)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_as_arrkom_missing_data(self):
        add_to_arrkom(self.user)
        event = generate_event(TYPE_CHOICES[0][0])
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.post(url)

        self.assertEqual(response.context['event'], event)
        self.assertInMessages(
            'Vi klarte ikke å sende mailene dine. Prøv igjen', response)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_ARRKOM='arrkom@online.ntnu.no')
    def test_post_as_arrkom_successfully(self):
        add_to_arrkom(self.user)
        event = generate_event(TYPE_CHOICES[0][0])
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.post(url, {
            'from_email': '1',
            'to_email': '1',
            'subject': 'Test',
            'message': 'Test message'
        })

        self.assertEqual(response.context['event'], event)
        self.assertInMessages(
            'Mailen ble sendt', response)
        self.assertEqual(mail.outbox[0].from_email, 'arrkom@online.ntnu.no')
        self.assertEqual(mail.outbox[0].subject, 'Test')
        self.assertIn('Test message', mail.outbox[0].body)

    def test_post_as_arrkom_invalid_from_email_defaults_to_kontakt(self):
        add_to_arrkom(self.user)
        event = generate_event(TYPE_CHOICES[0][0])
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.post(url, {
            'from_email': '1000',
            'to_email': '1',
            'subject': 'Test',
            'message': 'Test message'
        })

        self.assertEqual(response.context['event'], event)
        self.assertInMessages(
            'Mailen ble sendt', response)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'kontakt@online.ntnu.no')
        self.assertEqual(mail.outbox[0].subject, 'Test')
        self.assertIn('Test message', mail.outbox[0].body)

    def test_post_as_arrkom_invalid_to_email(self):
        add_to_arrkom(self.user)
        event = generate_event(TYPE_CHOICES[0][0])
        url = reverse('event_mail_participants', args=(event.id,))

        response = self.client.post(url, {
            'from_email': '1',
            'to_email': '1000',
            'subject': 'Test',
            'message': 'Test message'
        })

        self.assertEqual(response.context['event'], event)
        self.assertInMessages(
            'Vi klarte ikke å sende mailene dine. Prøv igjen', response)
        self.assertEqual(len(mail.outbox), 0)


class EventsArchive(TestCase):
    def test_events_index_empty(self):
        url = reverse('events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_index_exists(self):
        generate_event()

        url = reverse('events_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventsSearch(TestCase):
    def test_search_events(self):
        query = ''

        _url_pre_get_param = reverse('search_events')
        url = _url_pre_get_param + '?query=%s' % query

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventsCalendar(TestCase):
    def test_events_ics_all(self):
        url = reverse('events_ics')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_ics_specific_event(self):
        event = generate_event()

        url = reverse('event_ics', args=(event.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
