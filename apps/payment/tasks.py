import locale
import logging
from typing import List

from celery.schedules import crontab
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from pytz import timezone as tz

from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Attendee
from apps.marks.models import Mark, MarkUser, Suspension
from apps.payment.models import Payment, PaymentDelay
from onlineweb4.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        payment_reminder.s(),
    )

    sender.add_periodic_task(
        crontab(hour=7, minute=45),
        payment_delay_handler.s(),
    )


@app.task
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
            users_in_debt = not_paid(payment)
            if users_in_debt:
                send_deadline_passed_mail(payment, users_in_debt)
                notify_committee(payment, users_in_debt)
            for user in users_in_debt:
                set_mark(payment, user)
                suspend(payment, user)

            payment.active = False
            payment.save()
        elif deadline_diff < 259200:  # Remind them to pay 72 hours before the deadline
            delayed_users = not_paid(payment)
            if delayed_users:
                send_reminder_mail(payment, delayed_users)


def send_reminder_mail(payment: Payment, receivers: List[User]):
    subject = _("Betaling: ") + payment.description()

    content = render_to_string(
        "payment/email/reminder_notification.txt",
        {
            "payment_description": payment.description(),
            "payment_deadline": payment.deadline.astimezone(tz("Europe/Oslo")).strftime(
                "%-d %B %Y kl. %H:%M"
            ),
            "payment_url": settings.BASE_URL
            + payment.content_object.event.get_absolute_url(),
            "payment_email": payment.responsible_mail(),
        },
    )

    EmailMessage(
        subject,
        content,
        payment.responsible_mail(),
        [],
        [user.email for user in receivers],
    ).send()


def send_deadline_passed_mail(payment: Payment, receivers: List[User]):
    subject = _("Betalingsfrist utgått: ") + payment.description()

    content = render_to_string(
        "payment/email/reminder_deadline_passed.txt",
        {
            "payment_description": payment.description(),
            "payment_url": settings.BASE_URL
            + payment.content_object.event.get_absolute_url(),
            "payment_email": payment.responsible_mail(),
        },
    )

    EmailMessage(
        subject,
        content,
        payment.responsible_mail(),
        [],
        [user.email for user in receivers],
    ).send()


def notify_committee(payment: Payment, debted_users: List[User]):
    subject = _("Manglende betaling: ") + payment.description()

    content = render_to_string(
        "payment/email/payment_expired_list.txt",
        {
            "payment_description": payment.description(),
            "payment_users": debted_users,
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


def set_mark(payment: Payment, user: User):
    mark = Mark()
    mark.title = _("Manglende betaling på %s") % payment.description()
    mark.category = 6  # Manglende betaling
    mark.description = _(
        "Du har fått en prikk fordi du ikke har betalt for et arrangement."
    )
    mark.save()

    user_entry = MarkUser()
    user_entry.user = user
    user_entry.mark = mark
    user_entry.save()


def unattend(payment: Payment, user: User):
    Attendee.objects.get(event=payment.content_object, user=user).delete()


def suspend(payment: Payment, user: User):
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


@app.task
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


def handle_deadline_passed(payment_delay: PaymentDelay, unattend_deadline_passed: bool):
    set_mark(payment_delay.payment, payment_delay.user)
    if unattend_deadline_passed:
        suspend(payment_delay.payment, payment_delay.user)
    else:
        unattend(payment_delay.payment, payment_delay.user)

    payment_delay.active = False
    payment_delay.save()
    send_deadline_passed_mail_delay(payment_delay, unattend_deadline_passed)


def send_deadline_passed_mail_delay(
    payment_delay: PaymentDelay, unattend_deadline_passed: bool
):
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


def send_notification_mail(payment_delay: PaymentDelay, unattend_deadline_passed: bool):
    payment = payment_delay.payment

    subject = _("Husk betaling for ") + payment.description()

    valid_to = payment_delay.valid_to.astimezone(tz("Europe/Oslo"))

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
