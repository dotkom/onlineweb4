# -*- coding: utf-8 -*-

import locale
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _
from pytz import timezone as tz

from apps.events.models import AttendanceEvent, Attendee
from apps.marks.models import Mark, MarkUser, Suspension
from apps.mommy import schedule
from apps.mommy.registry import Task
from apps.payment.models import Payment, PaymentDelay


class PaymentReminder(Task):

    @staticmethod
    def run():
        logging.basicConfig()
        # logger = logging.getLogger()
        # logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        # All payments using deadline
        event_payments = Payment.objects.filter(
            payment_type=2, active=True,
            content_type=ContentType.objects.get_for_model(AttendanceEvent)
        )

        today = timezone.now()

        for payment in event_payments:

            # Number of days until the deadline
            deadline_diff = (payment.deadline.date() - today.date()).days

            if deadline_diff <= 0:
                if PaymentReminder.not_paid(payment):
                    PaymentReminder.send_deadline_passed_mail(payment)
                    PaymentReminder.notify_committee(payment)
                    PaymentReminder.set_marks(payment)

                payment.active = False
                payment.save()
            elif deadline_diff < 3:
                if PaymentReminder.not_paid(payment):
                    PaymentReminder.send_reminder_mail(payment)

    @staticmethod
    def send_reminder_mail(payment):
        subject = _("Betaling: ") + payment.description()

        content = render_to_string('payment/email/reminder_notification.txt', {
            'payment_description': payment.description(),
            'payment_deadline': payment.deadline.astimezone(tz('Europe/Oslo')).strftime("%-d %B %Y kl. %H:%M"),
            'payment_url': settings.BASE_URL + payment.content_object.event.get_absolute_url(),
            'payment_email': payment.responsible_mail()
        })

        receivers = PaymentReminder.not_paid_mail_addresses(payment)

        EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def send_deadline_passed_mail(payment):
        subject = _("Betalingsfrist utgått: ") + payment.description()

        content = render_to_string('payment/email/reminder_deadline_passed.txt', {
            'payment_description': payment.description(),
            'payment_url': settings.BASE_URL + payment.content_object.event.get_absolute_url(),
            'payment_email': payment.responsible_mail()
        })

        receivers = PaymentReminder.not_paid_mail_addresses(payment)

        EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def send_missed_payment_mail(payment):
        # NOTE
        # This method does nothing. Guess it was left here in cases rules for expired payments
        # were altered
        subject = _("Betalingsfrist utgått: ") + payment.description()
        message = _("Hei, du har ikke betalt for følgende arrangement: ") + payment.description()
        message += _("Fristen har utgått, og du har mistet plassen din på arrangementet")
        message += _("\nFor mer info om arrangementet se:")
        message += "\n" + str(settings.BASE_URL + payment.content_object.event.get_absolute_url())
        message += _("Dersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
        message += _("\n\nMvh\nLinjeforeningen Online")

        logging.getLogger(__name__).warn(
            'Call to method that does nothing. Should it send a mail? Subject: %s' % subject
        )

    @staticmethod
    def notify_committee(payment):
        subject = _("Manglende betaling: ") + payment.description()

        content = render_to_string('payment/email/payment_expired_list.txt', {
            'payment_description': payment.description(),
            'payment_users': PaymentReminder.not_paid(payment)
        })

        receivers = [payment.responsible_mail()]

        EmailMessage(subject, content, "online@online.ntnu.no", [], receivers).send()

    @staticmethod
    def not_paid(payment):
        attendees = [attendee.user for attendee in payment.content_object.attendees_qs]
        paid_users = payment.paid_users()

        # Creates a list of users in attendees but not in the list of paid users
        not_paid_users = [user for user in attendees if user not in paid_users]

        # Removes users with active payment delays from the list
        return [user for user in not_paid_users if user not in payment.payment_delay_users()]

    @staticmethod
    def not_paid_mail_addresses(payment):
        # Returns users in the list of attendees but not in the list of paid users
        return [user.email for user in PaymentReminder.not_paid(payment)]

    @staticmethod
    def set_marks(payment):
        mark = Mark()
        mark.title = _("Manglende betaling på %s") % payment.description()
        mark.category = 6  # Manglende betaling
        mark.description = _("Du har fått en prikk fordi du ikke har betalt for et arrangement.")
        mark.save()

        for user in PaymentReminder.not_paid(payment):
            user_entry = MarkUser()
            user_entry.user = user
            user_entry.mark = mark
            user_entry.save()

    @staticmethod
    def unattend(payment):
        for user in PaymentReminder.not_paid(payment):
            payment.content_object.notify_waiting_list(
                host=settings.BASE_URL, unattended_user=user)

            Attendee.objects.get(event=payment.content_object,
                                 user=user).delete()


class PaymentDelayHandler(Task):

    @staticmethod
    def run():
        logging.basicConfig()
        logger = logging.getLogger("feedback")
        logger.info("Payment delay handler started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        payment_delays = PaymentDelay.objects.filter(active=True)

        for payment_delay in payment_delays:
            unattend_deadline_passed = payment_delay.payment.content_object.unattend_deadline < payment_delay.valid_to
            if payment_delay.valid_to < timezone.now():
                PaymentDelayHandler.handle_deadline_passed(payment_delay, unattend_deadline_passed)
                logger.info("Deadline passed: " + str(payment_delay))
            elif (payment_delay.valid_to.date() - timezone.now().date()).days <= 2:
                PaymentDelayHandler.send_notification_mail(payment_delay, unattend_deadline_passed)
                logger.info("Notification sent to: " + str(payment_delay.user))

        # TODO handle committee notifying

    @staticmethod
    def handle_deadline_passed(payment_delay, unattend_deadline_passed):

        if unattend_deadline_passed:
            PaymentDelayHandler.set_mark(payment_delay)
            PaymentDelayHandler.handle_suspensions(payment_delay)
        else:
            PaymentDelayHandler.set_mark(payment_delay)
            PaymentDelayHandler.unattend(payment_delay)

        payment_delay.active = False
        payment_delay.save()
        PaymentDelayHandler.send_deadline_passed_mail(payment_delay, unattend_deadline_passed)

    @staticmethod
    def handle_suspensions(payment_delay):
        suspension = Suspension()

        suspension.title = "Manglende betaling"
        suspension.user = payment_delay.user
        suspension.payment_id = payment_delay.payment.id
        suspension.description = """
        Du har ikke betalt for et arangement du har vært med på. For å fjerne denne suspensjonen må du betale.\n
        Mer informasjon om betalingen finner du her: """
        suspension.description += str(
            settings.BASE_URL + payment_delay.payment.content_object.event.get_absolute_url()
        )

        suspension.save()

    @staticmethod
    def send_deadline_passed_mail(payment_delay, unattend_deadline_passed):
        payment = payment_delay.payment

        subject = _("Betalingsfrist utgått: ") + payment.description()

        content = render_to_string('payment/email/delay_reminder_deadline_passed.txt', {
            'payment_description': payment.description(),
            'payment_unattend_passed': unattend_deadline_passed,
            'payment_email': payment.responsible_mail()
        })

        receivers = [payment_delay.user.email]

        EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def send_notification_mail(payment_delay, unattend_deadline_passed):
        payment = payment_delay.payment
        
        subject = _("Husk betaling for ") + payment.description()

        valid_to = payment_delay.valid_to.astimezone(tz('Europe/Oslo'))

        # If event unattend deadline has not passed when payment deadline passes,
        # then the user will be automatically unattended, and given a mark.
        # Else, the unattend deadlline has passed, and the user will not be unattended,
        # but given a mark, and can't attend any other events untill payment is recived.
        content = render_to_string('payment/email/delay_reminder_notification.txt', {
            'payment_description': payment.description(),
            'payment_deadline': valid_to.strftime("%-d. %B %Y kl. %H:%M").encode("utf-8"),
            'payment_url': settings.BASE_URL + payment.content_object.event.get_absolute_url(),
            'payment_unattend_passed': unattend_deadline_passed,
            'payment_email': payment.responsible_mail()
        })

        receivers = [payment_delay.user.email]

        EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()

    @staticmethod
    def set_mark(payment_delay):
        mark = Mark()
        mark.title = _("Manglende betaling på %s") % payment_delay.payment.description()
        mark.category = 6  # Manglende betaling
        mark.description = _("Du har fått en prikk fordi du ikke har betalt for et arrangement.")
        mark.save()

        user_entry = MarkUser()
        user_entry.user = payment_delay.user
        user_entry.mark = mark
        user_entry.save()

    @staticmethod
    def unattend(payment_delay):
        payment_delay.payment.content_object.notify_waiting_list(
            host=settings.BASE_URL,
            unattended_user=payment_delay.user
        )
        Attendee.objects.get(event=payment_delay.payment.content_object, user=payment_delay.user).delete()

schedule.register(PaymentReminder, day_of_week='mon-sun', hour=7, minute=30)
schedule.register(PaymentDelayHandler, day_of_week='mon-sun', hour=7, minute=45)
