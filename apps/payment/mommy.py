#-*- coding: utf-8 -*-

import locale
import logging

from django.utils import timezone
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.conf import settings

from apps.payment.models import Payment, PaymentRelation, PaymentDelay
from apps.events.models import Event

from apps.mommy import Task, schedule

class PaymentReminder(Task):

    @staticmethod
    def run():
        logging.basicConfig()
        # logger = logging.getLogger("feedback")
        # logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        event_payments = Payment.objects.filter(instant_payment=False, active=True, 
            content_type=ContentType.objects.get_for_model(Event))

        today = timezone.now()

        for payment in event_payments:

            #Number of days until the deadline
            deadline_diff = (payment.deadline.date() - today.date()).days

            if deadline_diff <= 0:
                if PaymentReminder.not_paid(payment):
                    PaymentReminder.send_deadline_passed_mail(payment)
                    #TODO punish people
                    #TODO deactivate payment
                    PaymentReminder.notify_committee(payment)
            elif deadline_diff < 3:
                if PaymentReminder.not_paid(payment):
                    PaymentReminder.send_reminder_mail(payment)

    @staticmethod
    def send_reminder_mail(payment):
        subject = _(u"Betaling: ") + payment.description()
        
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.description()
        message += _(u"\nFristen for å betale er ") + str(payment.deadline.strftime("%-d %B %Y kl: %H:%M"))
        message += _(u"\nFor mer info om arrangement se:")
        message += "\n" + str(settings.BASE_URL + payment.content_object.get_absolute_url())
        #TODO add info about punishment for failed payments
        message += _(u"\n\nDersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

        receivers = PaymentReminder.not_paid_mail_addresses(payment)

        EmailMessage(subject, unicode(message), payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def send_deadline_passed_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.description()

        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.description()
        #message += _(u"fristen har utgått, og du får en prikk og 48 timer til å betale")
        #TODO add info about punishment
        message += _(u"\nFor mer info om arrangement se:")
        message += "\n" + str(settings.BASE_URL + payment.content_object.get_absolute_url())
        message += _(u"\nDersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

        receivers = PaymentReminder.not_paid_mail_addresses(payment)

        EmailMessage(subject, unicode(message), payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def send_missed_payment_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.description()
        message += _(u"fristen har utgått, og du har mistet plassen din på arrangement")
        message += _(u"\nFor mer info om arrangement se:")
        message += "\n" + str(settings.BASE_URL + payment.content_object.get_absolute_url())
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

    @staticmethod
    def notify_committee(payment):
        subject = _(u"Manglende betaling: ") + payment.description()
        message = _(u"Følgende brukere mangler betaling på ") + payment.description()
        message += u'\n'
        message += u'\n'.join([user.get_full_name() for user in PaymentReminder.not_paid(payment)])

        receivers = [payment.responsible_mail()]

        EmailMessage(subject, unicode(message), "online@online.ntnu.no", [], receivers).send()

    @staticmethod
    def not_paid(payment):
        event = payment.content_object
        attendees = [attendee.user for attendee in event.attendance_event.attendees_qs]
        paid_users = payment.paid_users()

        #Creates a list of users in attendees but not in the list of paid users
        not_paid_users = [user for user in attendees if user not in paid_users]

        #Remves users with active payment delays from the list
        return [user for user in not_paid_users if user not in payment.payment_delay_users()]

    @staticmethod
    def not_paid_mail_addresses(payment):
        #Returns users in the list of attendees but not in the list of paid users
        return [user.email for user in PaymentReminder.not_paid(payment)]


class PaymentDelayHandler(Task):

    @staticmethod
    def run():
        logging.basicConfig()
        # logger = logging.getLogger("feedback")
        # logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        payment_delays = PaymentDelay.objects.filter(active=True)

        for payment_delay in payment_delays:
            if payment_delay.valid_to < timezone.now():
                PaymentDelayHandler.handle_deadline_passed(payment_delay)


        #TODO handle committee notifying

    @staticmethod
    def handle_deadline_passed(payment_delay):
        #TODO punish user
        payment_delay.active = False
        payment_delay.save()
        PaymentDelayHandler.send_deadline_passed_mail(payment_delay)

    @staticmethod
    def send_deadline_passed_mail(payment_delay):
        payment = payment_delay.payment
        subject = _(u"Betalingsfrist utgått: ") + payment.description()

        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.description()

        #message += _(u"fristen har utgått, og du får en prikk og 48 timer til å betale")
        #TODO add info about punishment

        message += _(u"\nDersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

        receivers = [payment_delay.user.email]

        EmailMessage(subject, unicode(message), payment.responsible_mail(), [], receivers).send()


schedule.register(PaymentReminder, day_of_week='mon-sun', hour=21, minute=43)
schedule.register(PaymentDelayHandler, day_of_week='mon-sun', hour=17, minute=39)