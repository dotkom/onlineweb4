import logging
from zoneinfo import ZoneInfo

import icalendar
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ImproperlyConfigured
from django.core.signing import BadSignature, Signer
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from apps.authentication.models import OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.events.models import Event
from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users
from apps.payment.models import PaymentTypes
from utils.email import AutoChunkedEmailMessage, handle_mail_error


def handle_waitlist_bump(event, attendees, payment=None):
    title = f"Du har fått plass på {event.title}"

    message = f'Du har stått på venteliste for arrangementet "{str(event.title)}" og har nå fått plass.\n'

    if payment:
        message += _handle_waitlist_bump_payment(payment, attendees)
    else:
        message += (
            "Det kreves ingen ekstra handling fra deg med mindre du vil melde deg av."
        )

    message += "\n\nFor mer info:"
    message += f"\n{settings.BASE_URL}{event.get_absolute_url()}"

    send_message_to_users(
        title=title,
        content=message,
        recipients=[attendee.user for attendee in attendees],
        permission_type=PermissionType.WAIT_LIST_BUMP,
        url=event.get_absolute_url(),
    )


def _handle_waitlist_bump_payment(payment, attendees):
    extended_deadline = timezone.now() + timezone.timedelta(days=2)
    message = ""

    if payment.payment_type == PaymentTypes.IMMEDIATE:
        for attendee in attendees:
            payment.create_payment_delay(attendee.user, extended_deadline)
        message += "Dette arrangementet krever betaling og du må betale innen 48 timer."

    elif payment.payment_type == PaymentTypes.DEADLINE:
        if (
            payment.deadline > extended_deadline
        ):  # More than 2 days left of payment deadline
            message += "Dette arrangementet krever betaling og fristen for å betale er {}".format(
                payment.deadline.strftime("%-d %B %Y kl. %H:%M")
            )
        else:  # The deadline is in less than 2 days
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, extended_deadline)
            message += (
                "Dette arrangementet krever betaling og du har 48 timer på å betale"
            )

    elif payment.payment_type == PaymentTypes.DELAY:
        deadline = timezone.now() + payment.delay

        for attendee in attendees:
            payment.create_payment_delay(attendee.user, deadline)

        # Adding some seconds makes it seem like it's in more than X days, rather than X-1 days and 23 hours.
        # Could be weird if the delay is less than a minute or so, in which the seconds actually matter.
        message += (
            "Dette arrangementet krever betaling og du må betale innen {} ({}).".format(
                deadline.strftime("%-d %B %Y kl. %H:%M"),
                naturaltime(deadline + timezone.timedelta(seconds=5)),
            )
        )
    if len(payment.prices()) == 1:
        message += f"\nPrisen for dette arrangementet er {payment.prices()[0].price}kr."
    # elif len(payment.prices()) >= 2:
    #     message += "\nDette arrangementet har flere prisklasser:"
    #     for payment_price in payment.prices():
    #         message += "\n%s: %skr" % (payment_price.description, payment_price.price)
    return message


class Calendar:
    def __init__(self):
        self.cal = icalendar.Calendar()
        # Filename served by webserver
        self.filename = "online"
        # Required ical info
        self.cal.add("prodid", "-//Online//Onlineweb//EN")
        self.cal.add("version", "2.0")

    def add_event(self, event):
        raise NotImplementedError

    def add_events(self, events):
        for event in events:
            self.add_event(event)

    def output(self):
        """Return icalendar as text"""
        return self.cal.to_ical()

    def response(self):
        """Returns a response object"""
        response = HttpResponse(self.cal.to_ical(), content_type="text/calendar")
        response["Content-Type"] = "text/calendar; charset=utf-8"
        response["Content-Disposition"] = (
            "attachment; filename=" + self.filename + ".ics"
        )
        return response


class EventCalendar(Calendar):
    def user(self, user):
        """
        Personalized calendar
        This calendar is publicly available, but the url is not guessable so data should not be leaked to everyone
        """
        signer = Signer()
        try:
            username = signer.unsign(user)
            user = User.objects.get(username=username)
        except (BadSignature, User.DoesNotExist):
            user = None
        if user:
            # Getting all events that the user has/is participating in
            self.add_events(
                Event.objects.filter(attendance_event__attendees__user=user)
                .order_by("event_start")
                .prefetch_related("attendance_event", "attendance_event__attendees")
            )
            self.filename = username

    def event(self, event_id):
        """Single event"""
        try:
            self.add_event(Event.objects.get(id=event_id))
        except Event.DoesNotExist:
            pass
        self.filename = str(event_id)

    def events(self):
        """All events that haven't ended yet"""
        self.add_events(
            Event.objects.filter(event_end__gt=timezone.now()).order_by("event_start")
        )
        self.filename = "events"

    def add_event(self, event):
        cal_event = icalendar.Event()

        cal_event.add("dtstart", event.event_start)
        cal_event.add("dtend", event.event_end)
        cal_event.add("location", event.location)
        cal_event.add("summary", event.title)
        cal_event.add("description", event.ingress_short)
        cal_event.add("uid", "event-" + str(event.id) + "@online.ntnu.no")
        cal_event.add("url", f"https://online.ntnu.no/events/{event.id}")

        self.cal.add_component(cal_event)


def handle_attend_event_payment(event: Event, user: User):
    attendance_event = event.attendance_event
    payment = attendance_event.payment()

    if payment and not event.attendance_event.is_on_waitlist(user):
        if payment.payment_type == PaymentTypes.DELAY:
            deadline = timezone.now() + payment.delay
            payment.create_payment_delay(user, deadline)
        else:
            deadline = payment.deadline

        # Send notification about payment to user by mail
        subject = f"[{event.title}] Husk å betale for å fullføre påmeldingen til arrangementet."

        content = render_to_string(
            "events/email/payment_reminder.txt",
            {
                "event": event.title,
                "time": deadline.astimezone(ZoneInfo("Europe/Oslo")).strftime(
                    "%-d %B %Y kl. %H:%M"
                ),
                "price": payment.price().price,
            },
        )

        send_message_to_users(
            title=subject,
            content=content,
            from_email=event.feedback_mail(),
            recipients=[user],
            permission_type=PermissionType.DEFAULT,
            url=event.get_absolute_url(),
        )


def handle_mail_participants(
    event,
    _to_email_value,
    subject,
    _message,
    _images,
    all_attendees,
    attendees_on_waitlist,
    attendees_not_paid,
):
    logger = logging.getLogger(__name__)

    _to_email_options = {
        "1": (all_attendees, "all attendees"),
        "2": (attendees_on_waitlist, "attendees on waitlist"),
        "3": (attendees_not_paid, "attendees not paid"),
    }

    from_email = "kontakt@online.ntnu.no"
    organizer_group: OnlineGroup = OnlineGroup.objects.filter(
        group=event.organizer
    ).first()
    if organizer_group and organizer_group.email:
        from_email = organizer_group.email

    if _to_email_value not in _to_email_options:
        return False
    # Who to send emails to
    user_recipients = _to_email_options[_to_email_value][0]
    signature = f"\n\nVennlig hilsen Linjeforeningen Online.\n(Denne eposten kan besvares til {from_email})"

    message = f"{_message}{signature}"

    # Send mail
    try:
        email = AutoChunkedEmailMessage(
            str(subject),
            str(message),
            from_email,
            [from_email],
            [a.user.email for a in user_recipients],
            attachments=(_images),
        )
        email.send_in_background(
            error_callback=lambda e, nse, se: handle_mail_error(
                e, nse, se, [from_email]
            )
        )

        logger.info(
            f'Sent mail to {_to_email_options[_to_email_value][1]} for event "{event}".'
        )
        return all_attendees, attendees_on_waitlist, attendees_not_paid
    except ImproperlyConfigured as e:
        logger.error(
            f'Something went wrong while trying to send mail to {_to_email_options[_to_email_value][1]} for event "{event}"\n{e}'
        )
