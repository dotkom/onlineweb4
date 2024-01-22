# -*- coding: utf-8 -*-

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TransactionTestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Attendee, Event
from apps.notifications.constants import PermissionType
from apps.notifications.models import Permission
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation
from apps.payment.mommy import handle_deadline_passed, not_paid, not_paid_mail_addresses


class PaymentTest(TransactionTestCase):
    def setUp(self):
        G(
            Permission,
            permission_type=PermissionType.RECEIPT,
            force_email=True,
            allow_email=True,
        )
        self.event: Event = G(Event, title="Sjakkturnering")
        self.attendance_event: AttendanceEvent = G(
            AttendanceEvent,
            event=self.event,
            unattend_deadline=timezone.now() + timedelta(days=1),
        )
        self.user: User = G(
            User,
            username="ola123",
            ntnu_username="ola123ntnu",
            first_name="ola",
            last_name="nordmann",
        )
        G(Email, user=self.user, primary=True)

        self.event_payment = G(
            Payment,
            object_id=self.event.id,
            content_type=ContentType.objects.get_for_model(AttendanceEvent),
        )
        self.payment_price = G(PaymentPrice, price=200, payment=self.event_payment)

    def simulate_user_payment(self, user):
        G(
            PaymentRelation,
            payment=self.event_payment,
            user=user,
            payment_price=self.payment_price,
        )
        self.event_payment.handle_payment(user)

    def test_payment_creation(self):
        PaymentRelation.objects.create(
            payment=self.event_payment, payment_price=self.payment_price, user=self.user
        )
        payment_relation = PaymentRelation.objects.all()[0]

        self.assertEqual(payment_relation.user, self.user)
        self.assertEqual(payment_relation.payment, self.event_payment)

    def test_event_description(self):
        self.assertEqual(self.event_payment.description(), "Sjakkturnering")

    def test_event_post_payment_create_attendee(self):
        self.event_payment.handle_payment(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertEqual(attendee.user, self.user)
        self.assertEqual(attendee.event, self.attendance_event)

    def test_event_payment_complete_modify_attendee(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.event_payment.handle_payment(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertTrue(attendee.paid)

    def test_event_payment_receipt(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "[Kvittering] " + payment_relation.payment.description(),
        )
        self.assertEqual(mail.outbox[0].to, [payment_relation.user.email])

    def test_event_payment_refund_check_unattend_deadline_passed(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )

        self.attendance_event.unattend_deadline = timezone.now() - timedelta(days=1)
        self.attendance_event.save()

        self.assertFalse(payment_relation.is_refundable)

    def test_event_payment_refund_check_attendee_exists(self):
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )

        self.assertFalse(payment_relation.is_refundable)

    def test_event_payment_refund_check_event_started(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )

        self.event.event_start = timezone.now() - timedelta(days=1)
        self.event.save()

        self.assertFalse(payment_relation.is_refundable)

    def test_event_payment_refund_check(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.attendance_event.unattend_deadline = timezone.now() + timedelta(days=1)
        self.attendance_event.save()

        self.event.event_start = timezone.now() + timedelta(days=1)
        self.event.save()

        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )

        self.assertTrue(payment_relation.is_refundable)

    def test_event_payment_refund(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.event_payment.handle_payment(self.user)

        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price,
        )
        self.assertFalse(payment_relation.refunded)

        payment_relation.refund()
        attendees = Attendee.objects.all()

        self.assertTrue(payment_relation.refunded)
        self.assertEqual(set([]), set(attendees))

    # Mommy

    def test_event_mommy_not_paid(self):
        user1 = G(User)
        user2 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        self.simulate_user_payment(user1)

        self.assertEqual([user2], not_paid(self.event_payment))

    def test_event_mommy_paid(self):
        user1 = G(User)
        user2 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        self.simulate_user_payment(user1)
        self.simulate_user_payment(user2)

        result = [
            attendee.user
            for attendee in self.event_payment.content_object.attending_attendees_qs
            if attendee.paid
        ]
        expected = [user1, user2]
        self.assertEqual(expected, result)

    def test_event_mommy_paid_with_delays(self):
        user1 = G(User)
        user2 = G(User)
        user3 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        G(Attendee, event=self.attendance_event, user=user3)
        G(
            PaymentDelay,
            payment=self.event_payment,
            user=user2,
            valid_to=timezone.now() + timedelta(days=1),
        )
        self.simulate_user_payment(user3)

        self.assertEqual([user1], not_paid(self.event_payment))

    def test_event_mommy_not_paid_mail_address(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        not_paid_email = not_paid_mail_addresses(self.event_payment)

        self.assertEqual([self.user.email], not_paid_email)

    def test_mommy_payment_delay(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_delay = G(
            PaymentDelay,
            payment=self.event_payment,
            user=self.user,
            valid_to=timezone.now() + timedelta(days=1),
        )

        self.assertTrue(payment_delay.active)

        handle_deadline_passed(payment_delay, False)

        self.assertFalse(payment_delay.active)

    def test_mommy_payment_delay_excluding(self):
        G(Attendee, event=self.attendance_event, user=self.user)

        self.assertEqual([self.user], not_paid(self.event_payment))

        G(
            PaymentDelay,
            payment=self.event_payment,
            user=self.user,
            valid_to=timezone.now() + timedelta(days=1),
        )

        self.assertFalse(not_paid(self.event_payment))

    # TODO Test waislist bump
