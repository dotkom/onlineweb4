from django.test import TestCase
from django_dynamic_fixture import G
from django.contrib.contenttypes.models import ContentType

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.payment.models import Payment, PaymentRelation

class PaymentTest(TestCase):

    def setUp(self):
        self.event = G(Event, title='Sjakkturnering')
        self.attendance_event = G(AttendanceEvent, event=self.event)
        self.user = G(User, username = 'ola123', ntnu_username = 'ola123ntnu', first_name = "ola", last_name = "nordmann")

        self.event_payment = G(Payment, object_id=self.event.id, content_type=ContentType.objects.get_for_model(Event), price=200 )

    def testPaymentCreation(self):
        PaymentRelation.objects.create(payment=self.event_payment, user=self.user)
        payment_relation = PaymentRelation.objects.all()[0]

        self.assertEqual(payment_relation.user, self.user)
        self.assertEqual(payment_relation.payment, self.event_payment)

    def testEventDescription(self):
        self.assertEqual(self.event_payment.content_object.payment_description(), "Sjakkturnering")

    def testEventPostPaymentCreateAttendee(self):
        self.event_payment.content_object.payment_complete(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertEqual(attendee.user, self.user)
        self.assertEqual(attendee.event, self.attendance_event)


    def testEventPaymentCompleteModifyAttendee(self):
        G(Attendee, event=self.attendance_event, user=self.user)
        self.event_payment.content_object.payment_complete(self.user)

        attendee = Attendee.objects.all()[0]

        self.assertTrue(attendee.paid)



