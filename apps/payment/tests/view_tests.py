# -*- coding: utf-8 -*-

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Attendee, Event
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation
from apps.payment.mommy import PaymentDelayHandler, PaymentReminder


class PaymentTest(TestCase):

    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(
            AttendanceEvent,
            event=self.event,
            unnatend_deadline=timezone.now() + timedelta(days=1)
        )
        self.user = G(
            User,
            username='ola123',
            ntnu_username='ola123ntnu',
            first_name="ola",
            last_name="nordmann"
        )

        self.event_payment = G(
            Payment,
            object_id=self.event.id,
            content_type=ContentType.objects.get_for_model(AttendanceEvent)
        )
        self.payment_price = G(PaymentPrice, price=200, payment=self.event_payment)

    def simulate_user_payment(self, user):
        G(PaymentRelation, payment=self.event_payment,
          user=user, payment_price=self.payment_price)
        self.event_payment.handle_payment(user)

    def testPaymentCreation(self):
        PaymentRelation.objects.create(
            payment=self.event_payment,
            payment_price=self.payment_price,
            user=self.user
        )
        payment_relation = PaymentRelation.objects.all()[0]

        self.assertEqual(payment_relation.user, self.user)
        self.assertEqual(payment_relation.payment, self.event_payment)

    def testEventDescription(self):
        self.assertEqual(self.event_payment.description(), "Sjakkturnering")

    def testEventPostPaymentCreateAttendee(self):
        self.event_payment.handle_payment(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertEqual(attendee.user, self.user)
        self.assertEqual(attendee.event, self.attendance_event)

    def testEventPaymentCompleteModifyAttendee(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.event_payment.handle_payment(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertTrue(attendee.paid)

    def testEventPaymentReceipt(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[Kvittering] " + payment_relation.payment.description())
        self.assertEqual(mail.outbox[0].to, [payment_relation.user.email])

    def testEventPaymentRefundCheckUnatendDeadlinePassed(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )

        self.attendance_event.unattend_deadline = timezone.now() - timedelta(days=1)
        self.attendance_event.save()

        self.assertFalse(self.event_payment.check_refund(payment_relation)[0])

    def testEventPaymentRefundCheckAtendeeExists(self):
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )

        self.assertFalse(self.event_payment.check_refund(payment_relation)[0])

    def testEventPaymentRefundCheckEventStarted(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )

        self.event.event_start = timezone.now() - timedelta(days=1)
        self.event.save()

        self.assertFalse(self.event_payment.check_refund(payment_relation)[0])

    def testEventPaymentRefundCheck(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.attendance_event.unattend_deadline = timezone.now() + timedelta(days=1)
        self.attendance_event.save()

        self.event.event_start = timezone.now() + timedelta(days=1)
        self.event.save()

        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )

        print(self.event_payment.check_refund(payment_relation))
        self.assertTrue(self.event_payment.check_refund(payment_relation)[0])

    def testEventPaymentRefund(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.event_payment.handle_payment(self.user)

        payment_relation = G(
            PaymentRelation,
            payment=self.event_payment,
            user=self.user,
            payment_price=self.payment_price
        )
        self.assertFalse(payment_relation.refunded)

        self.event_payment.handle_refund(payment_relation)
        attendees = Attendee.objects.all()

        self.assertTrue(payment_relation.refunded)
        self.assertEqual(set([]), set(attendees))

    # Mommy

    def testEventMommyNotPaid(self):
        user1 = G(User)
        user2 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        self.simulate_user_payment(user1)

        not_paid = PaymentReminder.not_paid(self.event_payment)

        self.assertEqual([user2], not_paid)

    def testEventMommyPaid(self):
        user1 = G(User)
        user2 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        self.simulate_user_payment(user1)
        self.simulate_user_payment(user2)

        not_paid = PaymentReminder.not_paid(self.event_payment)

        self.assertFalse(not_paid)

    def testEventMommyPaidWithDelays(self):
        user1 = G(User)
        user2 = G(User)
        user3 = G(User)
        G(Attendee, event=self.attendance_event, user=user1)
        G(Attendee, event=self.attendance_event, user=user2)
        G(Attendee, event=self.attendance_event, user=user3)
        G(PaymentDelay, payment=self.event_payment, user=user2,
          valid_to=timezone.now() + timedelta(days=1))
        self.simulate_user_payment(user3)

        not_paid = PaymentReminder.not_paid(self.event_payment)

        self.assertEqual([user1], not_paid)

    def testEventMommyNotPaidMailAddress(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        not_paid_email = PaymentReminder.not_paid_mail_addresses(self.event_payment)

        self.assertEqual([self.user.email], not_paid_email)

    def testMommyPaymentDelay(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        payment_delay = G(
            PaymentDelay,
            payment=self.event_payment,
            user=self.user,
            valid_to=timezone.now() + timedelta(days=1)
        )

        self.assertTrue(payment_delay.active)

        PaymentDelayHandler.handle_deadline_passed(payment_delay, False)

        self.assertFalse(payment_delay.active)

    def testMommyPaymentDelayExcluding(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        not_paid = PaymentReminder.not_paid(self.event_payment)

        self.assertEqual([self.user], not_paid)

        G(
            PaymentDelay,
            payment=self.event_payment,
            user=self.user,
            valid_to=timezone.now() + timedelta(days=1)
        )

        not_paid = PaymentReminder.not_paid(self.event_payment)

        self.assertFalse(not_paid)

    # TODO Test waislist bump
