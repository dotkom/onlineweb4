#-*- coding: utf-8 -*-

import locale
import logging

from django.utils import timezone
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event
from apps.mommy import Task, schedule

class PaymentReminder(Task):

    @staticmethod
    def run():
        logging.basicConfig()
        # logger = logging.getLogger("feedback")
        # logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        event_payments = Payment.objects.filter (instant_payment=False, active=True, content_type=ContentType.objects.get_for_model(Event))

        today = timezone.now()

        for payment in event_payments:

            deadline_diff = (payment.deadline - today).days

            print deadline_diff

            if deadline_diff <= 0:
                i = 1
                #TODO do stuff
            elif deadline_diff < 3:
                if PaymentReminder.not_paid(payment):
                    PaymentReminder.send_reminder_mail(payment)

    @staticmethod
    def send_reminder_mail(payment):
        subject = _(u"Betaling: ") + payment.content_object_description()
        
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"\nFristen for og betale er ") + str(payment.deadline)
        #TODO add info about punishment for failed payments
        message += _(u"\n\nDersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

        receivers = [user.email for user in PaymentReminder.not_paid(payment)]

        EmailMessage(subject, unicode(message), payment.content_object_mail(), [], receivers).send()

    @staticmethod
    def send_deadline_passed_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.content_object_description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"fristen har utgått, og du får en prikk og 48 timer til å betale")
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

    @staticmethod
    def send_missed_payment_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.content_object_description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"fristen har utgått, og du har mistet plassen din på arrangement")
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

    @staticmethod
    def not_paid(payment):
        event = payment.content_object
        attendees = [attendee.user for attendee in event.attendance_event.attendees_qs]
        paid_users = payment.paid_users()

        #Returns users in the list of attendees but not in the list of paid users
        return [user for user in attendees if user not in paid_users]


schedule.register(PaymentReminder, day_of_week='mon-sun', hour=18, minute=55)
