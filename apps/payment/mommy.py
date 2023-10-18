# -*- coding: utf-8 -*-

import locale
import logging
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.events.models import AttendanceEvent, Attendee
from apps.marks.models import Mark, MarkUser, Suspension
from apps.payment.models import Payment, PaymentDelay
from utils.email import AutoChunkedEmailMessage, handle_mail_error


def payment_reminder():
    logging.basicConfig()
    # logger = logging.getLogger()
    # logger.info("Event payment job started")
    locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

    # All payments using deadline
    event_payments = Payment.objects.filter(
        payment_type=2,
        active=True,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
    )

    today = timezone.now()

    for payment in event_payments:
        # Number of days until the deadline
        deadline_diff = (payment.deadline - today).seconds

        if deadline_diff <= 0:
            if not_paid(payment):
                send_deadline_passed_mail(payment)
                notify_committee(payment)
                set_marks(payment)
                suspend(payment)

            payment.active = False
            payment.save()
        elif (
            deadline_diff < 24 * 60 * 60 * 3
        ):  # Remind them to pay 72 hours before the deadline
            if not_paid(payment):
                send_reminder_mail(payment)


def send_reminder_mail(payment):
    subject = _("Betaling: ") + payment.description()

    content = render_to_string(
        "payment/email/reminder_notification.txt",
        {
            "payment_description": payment.description(),
            "payment_deadline": payment.deadline.astimezone(
                ZoneInfo("Europe/Oslo")
            ).strftime("%-d %B %Y kl. %H:%M"),
            "payment_url": settings.BASE_URL
            + payment.content_object.event.get_absolute_url(),
            "payment_email": payment.responsible_mail(),
        },
    )

    receivers = not_paid_mail_addresses(payment)

    email = AutoChunkedEmailMessage(
        subject=subject,
        body=content,
        from_email=payment.responsible_mail(),
        to=[],
        bcc=receivers,
    )
    email.send_in_background(
        error_callback=lambda e, nse, se: handle_mail_error(
            e, nse, se, to=[payment.responsible_mail()]
        )
    )


def send_missed_payment_mail(payment):
    # NOTE
    # This method does nothing. Guess it was left here in cases rules for expired payments
    # were altered
    subject = _("Betalingsfrist utgått: ") + payment.description()
    message = (
        _("Hei, du har ikke betalt for følgende arrangement: ") + payment.description()
    )
    message += _("Fristen har gått ut, og du har mistet plassen din på arrangementet")
    message += _("\nFor mer info om arrangementet se:")
    message += "\n" + str(
        settings.BASE_URL + payment.content_object.event.get_absolute_url()
    )
    message += (
        _("Dersom du har spørsmål kan du sende mail til ") + payment.responsible_mail()
    )
    message += _("\n\nMvh\nLinjeforeningen Online")

    logging.getLogger(__name__).warn(
        "Call to method that does nothing. Should it send a mail? Subject: %s" % subject
    )


def notify_committee(payment):
    subject = _("Manglende betaling: ") + payment.description()

    content = render_to_string(
        "payment/email/payment_expired_list.txt",
        {
            "payment_description": payment.description(),
            "payment_users": not_paid(payment),
        },
    )

    receivers = [payment.responsible_mail()]

    EmailMessage(subject, content, "online@online.ntnu.no", [], receivers).send()


def not_paid(payment):
    attendees = payment.content_object.attending_attendees_qs
    not_paid_users = [attendee.user for attendee in attendees if not attendee.paid]

    # Removes users with active payment delays from the list
    return [
        user for user in not_paid_users if user not in payment.payment_delay_users()
    ]


def not_paid_mail_addresses(payment):
    # Returns users in the list of attendees but not in the list of paid users
    return [user.email for user in not_paid(payment)]


def set_marks(payment):
    mark = Mark()
    mark.title = _("Manglende betaling på %s") % payment.description()
    mark.category = 6  # Manglende betaling
    mark.description = _(
        "Du har fått en prikk fordi du ikke har betalt for et arrangement."
    )
    mark.save()

    for user in not_paid(payment):
        user_entry = MarkUser()
        user_entry.user = user
        user_entry.mark = mark
        user_entry.save()


def suspend(payment):
    for user in not_paid(payment):
        suspension = Suspension()

        suspension.title = "Manglende betaling"
        suspension.user = user
        suspension.payment_id = payment.id
        suspension.description = """
        Du har ikke betalt for et arangement du har vært med på. For å fjerne denne suspensjonen må du betale.\n
        Mer informasjon om betalingen finner du her: """
        suspension.description += str(
            settings.BASE_URL + payment.content_object.event.get_absolute_url()
        )

        suspension.save()


def payment_delay_handler():
    logging.basicConfig()
    logger = logging.getLogger("feedback")
    logger.info("Payment delay handler started")
    locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

    payment_delays = PaymentDelay.objects.filter(active=True)

    for payment_delay in payment_delays:
        unattend_deadline_passed = (
            payment_delay.payment.content_object.unattend_deadline
            < payment_delay.valid_to
        )
        if payment_delay.valid_to < timezone.now():
            handle_deadline_passed(payment_delay, unattend_deadline_passed)
            logger.info("Deadline passed: " + str(payment_delay))
        elif (payment_delay.valid_to.date() - timezone.now().date()).days <= 2:
            send_notification_mail(payment_delay, unattend_deadline_passed)
            logger.info("Notification sent to: " + str(payment_delay.user))

    # TODO handle committee notifying


def handle_deadline_passed(payment_delay, unattend_deadline_passed):
    if unattend_deadline_passed:
        set_mark(payment_delay)
        handle_suspensions(payment_delay)
    else:
        set_mark(payment_delay)
        unattend(payment_delay)

    payment_delay.active = False
    payment_delay.save()
    send_deadline_passed_mail(payment_delay, unattend_deadline_passed)


def handle_suspensions(payment_delay):
    suspension = Suspension()

    suspension.title = "Manglende betaling"
    suspension.user = payment_delay.user
    suspension.payment_id = payment_delay.payment.id
    suspension.description = """
    Du har ikke betalt for et arangement du har vært med på. For å fjerne denne suspensjonen må du betale.\n
    Mer informasjon om betalingen finner du her: """
    suspension.description += str(
        settings.BASE_URL
        + payment_delay.payment.content_object.event.get_absolute_url()
    )

    suspension.save()


def send_deadline_passed_mail(payment_delay, unattend_deadline_passed=True):
    payment = payment_delay.payment

    subject = _("Betalingsfrist utgått: ") + payment.description()

    content = render_to_string(
        "payment/email/delay_reminder_deadline_passed.txt",
        {
            "payment_description": payment.description(),
            "payment_unattend_passed": unattend_deadline_passed,
            "payment_email": payment.responsible_mail(),
        },
    )

    receivers = [payment_delay.user.email]

    EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()


def send_notification_mail(payment_delay, unattend_deadline_passed):
    payment = payment_delay.payment

    subject = _("Husk betaling for ") + payment.description()

    valid_to = payment_delay.valid_to.astimezone(ZoneInfo("Europe/Oslo"))

    # If event unattend deadline has not passed when payment deadline passes,
    # then the user will be automatically unattended, and given a mark.
    # Else, the unattend deadlline has passed, and the user will not be unattended,
    # but given a mark, and can't attend any other events untill payment is recived.
    content = render_to_string(
        "payment/email/delay_reminder_notification.txt",
        {
            "payment_description": payment.description(),
            "payment_deadline": valid_to.strftime("%-d. %B %Y kl. %H:%M").encode(
                "utf-8"
            ),
            "payment_url": settings.BASE_URL
            + payment.content_object.event.get_absolute_url(),
            "payment_unattend_passed": unattend_deadline_passed,
            "payment_email": payment.responsible_mail(),
        },
    )

    receivers = [payment_delay.user.email]

    EmailMessage(subject, content, payment.responsible_mail(), [], receivers).send()


def set_mark(payment_delay):
    mark = Mark()
    mark.title = _("Manglende betaling på %s") % payment_delay.payment.description()
    mark.category = 6  # Manglende betaling
    mark.description = _(
        "Du har fått en prikk fordi du ikke har betalt for et arrangement."
    )
    mark.save()

    user_entry = MarkUser()
    user_entry.user = payment_delay.user
    user_entry.mark = mark
    user_entry.save()


def unattend(payment_delay):
    Attendee.objects.get(
        event=payment_delay.payment.content_object, user=payment_delay.user
    ).delete()
