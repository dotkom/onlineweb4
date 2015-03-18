import locale
import logging

from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event
from apps.mommy import Task, schedule

class PaymentReminder(Task):

    @staticmethod
    def run():
        logger = logging.getLogger()
        logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        event_payments = active_event_payments()

        today = timezone.now()

        for payment in event_payments:

            deadline_diff = (payment.deadline - today).days

            if deadline_diff <= 0:
                i = 1
                #TODO do stuff
            elif deadline_diff < 3:
                send_remainder_mail(payment)
            



    @staticmethod
    def active_event_payments():
        return Payment.objects.filter (instant_payment=False, active=True, content_type=ContentType.objects.get_for_model(Event))

    def send_remainder_mail(payment):
        i = 1
        #TODO

    @staticmethod
    def not_paid(payment):
        event = payment.content_object
        attendees = [attendee.user for attendee in event.attendance_event.attendees_qs]
        paid_users = payment.paid_users()

        return [user for user in attendees if user not in paid_users]



schedule.register(PaymentReminder, day_of_week='mon-sun', hour=7, minute=05)
