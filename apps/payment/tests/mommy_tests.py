from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import F, G

from apps.authentication.models import OnlineGroup
from apps.events.tests.utils import attend_user_to_event, generate_event, generate_user
from apps.payment.models import PaymentTypes
from apps.payment.mommy import payment_reminder
from apps.payment.tests.utils import generate_event_payment


class PaymentReminderTests(TestCase):
    def setup_testcase(self):
        self.committee = G(
            OnlineGroup, group=F(name="Arrkom"), email="arrkom@online.ntnu.no"
        )
        self.user = generate_user(username="test_user", email="oline@online.online")

        self.event = generate_event(organizer=self.committee.group)
        self.event.event_end = timezone.now() - timezone.timedelta(days=3)
        self.event.event_start = timezone.now() - timezone.timedelta(days=2)
        self.event.attendance_event.registration_end = (
            timezone.now() - timezone.timedelta(days=1)
        )
        self.event.attendance_event.unattend_deadline = (
            timezone.now() - timezone.timedelta(days=1)
        )
        self.event.save()
        self.event.attendance_event.save()

        self.payment = generate_event_payment(
            self.event,
            deadline=timezone.now() - timezone.timedelta(days=1),
            payment_type=PaymentTypes.DEADLINE,
        )
        self.attendee = attend_user_to_event(self.event, self.user)

    def test_no_attend_no_mail(self):
        payment_reminder()
        self.assertEqual(len(mail.outbox), 0)

    def test_attend_mail(self):
        self.setup_testcase()
        payment_reminder()
        self.assertEqual(len(mail.outbox), 2)
        user_mail, committee_mail = mail.outbox
        self.assertEqual(user_mail.bcc, [self.user.email])
        self.assertEqual(committee_mail.to, [self.committee.email])
