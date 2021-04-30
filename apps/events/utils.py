# -*- coding: utf-8 -*-
import logging

import icalendar
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.signing import BadSignature, Signer
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from pytz import timezone as tz

from apps.authentication.models import OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.events.models import Attendee, Event, Extras
from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users
from apps.payment.models import PaymentDelay, PaymentRelation


def handle_waitlist_bump(event, attendees, payment=None):
    title = "Du har fått plass på %s" % (event.title)

    message = (
        'Du har stått på venteliste for arrangementet "%s" og har nå fått plass.\n'
        % (str(event.title))
    )

    if payment:
        message += _handle_waitlist_bump_payment(payment, attendees)
    else:
        message += (
            "Det kreves ingen ekstra handling fra deg med mindre du vil melde deg av."
        )

    message += "\n\nFor mer info:"
    message += "\n%s%s" % (settings.BASE_URL, event.get_absolute_url())

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

    if payment.payment_type == 1:  # Instant
        for attendee in attendees:
            payment.create_payment_delay(attendee.user, extended_deadline)
        message += "Dette arrangementet krever betaling og du må betale innen 48 timer."

    elif payment.payment_type == 2:  # Deadline
        if (
            payment.deadline > extended_deadline
        ):  # More than 2 days left of payment deadline
            message += (
                "Dette arrangementet krever betaling og fristen for å betale er %s"
                % (payment.deadline.strftime("%-d %B %Y kl. %H:%M"))
            )
        else:  # The deadline is in less than 2 days
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, extended_deadline)
            message += (
                "Dette arrangementet krever betaling og du har 48 timer på å betale"
            )

    elif payment.payment_type == 3:  # Delay
        deadline = timezone.now() + payment.delay
        for attendee in attendees:
            payment.create_payment_delay(attendee.user, deadline)

        # Adding some seconds makes it seem like it's in more than X days, rather than X-1 days and 23 hours.
        # Could be weird if the delay is less than a minute or so, in which the seconds actually matter.
        message += (
            "Dette arrangementet krever betaling og du må betale innen %s (%s)."
            % (
                deadline.strftime("%-d %B %Y kl. %H:%M"),
                naturaltime(deadline + timezone.timedelta(seconds=5)),
            )
        )
    if len(payment.prices()) == 1:
        message += (
            "\nPrisen for dette arrangementet er %skr." % payment.prices()[0].price
        )
    # elif len(payment.prices()) >= 2:
    #     message += "\nDette arrangementet har flere prisklasser:"
    #     for payment_price in payment.prices():
    #         message += "\n%s: %skr" % (payment_price.description, payment_price.price)
    return message


class Calendar(object):
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

        self.cal.add_component(cal_event)


def handle_attendance_event_detail(event, user, context):
    attendance_event = event.attendance_event

    user_anonymous = True
    user_attending = False
    attendee = False
    place_on_wait_list = 0
    will_be_on_wait_list = False
    can_unattend = True
    rules = []
    user_status = False
    show_as_attending = False
    user_setting_show_as_attending = False

    if attendance_event.rule_bundles:
        for rule_bundle in attendance_event.rule_bundles.all():
            rules.append(rule_bundle.rule_strings)

    if user.is_authenticated:
        user_anonymous = False
        if attendance_event.is_attendee(user):
            user_attending = True
            attendee = Attendee.objects.get(event=attendance_event, user=user)
            show_as_attending = attendee.show_as_attending_event

        will_be_on_wait_list = attendance_event.will_i_be_on_wait_list

        can_unattend = timezone.now() < attendance_event.registration_end

        user_status = event.attendance_event.is_eligible_for_signup(user)

        # Check if this user is on the waitlist
        place_on_wait_list = attendance_event.what_place_is_user_on_wait_list(user)

        # Get the default setting for visible as attending event from users privacy setting
        user_setting_show_as_attending = user.get_visible_as_attending_events()

    context.update(
        {
            "now": timezone.now(),
            "attendance_event": attendance_event,
            "user_anonymous": user_anonymous,
            "attendee": attendee,
            "user_attending": user_attending,
            "will_be_on_wait_list": will_be_on_wait_list,
            "can_unattend": can_unattend,
            "rules": rules,
            "user_status": user_status,
            "place_on_wait_list": int(place_on_wait_list),
            "user_setting_show_as_attending": user_setting_show_as_attending,
            "show_as_attending": show_as_attending,
            # 'position_in_wait_list': position_in_wait_list,
        }
    )
    return context


def handle_event_payment(event, user, payment, context):
    user_paid = False
    payment_delay = None
    payment_relation_id = None

    context.update(
        {
            "payment": payment,
            "user_paid": user_paid,
            "payment_delay": payment_delay,
            "payment_relation_id": payment_relation_id,
        }
    )

    if (
        not user.is_authenticated
    ):  # Return early if user not logged in, can't filter payment relations against no one
        return context

    payment_relations = PaymentRelation.objects.filter(
        payment=payment, user=user, refunded=False
    )
    for payment_relation in payment_relations:
        user_paid = True
        payment_relation_id = payment_relation.id
    if not user_paid and context["user_attending"]:
        attendee = Attendee.objects.get(event=event.attendance_event, user=user)
        if attendee:
            user_paid = attendee.paid

    if not user_paid:
        payment_delays = PaymentDelay.objects.filter(user=user, payment=payment)
        if payment_delays:
            payment_delay = payment_delays[0]

    context.update(
        {
            "user_paid": user_paid,
            "payment_delay": payment_delay,
            "payment_relation_id": payment_relation_id,
        }
    )

    return context


def handle_event_ajax(event, user, action, extras_id):
    if action == "extras":
        return handle_event_extras(event, user, extras_id)
    else:
        raise NotImplementedError


def handle_event_extras(event, user, extras_id):
    resp = {"message": "Feil!"}

    if not event.is_attendance_event():
        return {"message": "Dette er ikke et påmeldingsarrangement."}

    attendance_event = event.attendance_event

    if not attendance_event.is_attendee(user):
        return {"message": "Du er ikke påmeldt dette arrangementet."}

    attendee = Attendee.objects.get(event=attendance_event, user=user)
    try:
        attendee.extras = attendance_event.extras.get(id=extras_id)
    except Extras.DoesNotExist:
        return {"message": "Ugyldig valg"}

    attendee.save()
    resp["message"] = "Lagret ditt valg"
    return resp


def handle_attend_event_payment(event: Event, user: User):
    attendance_event = event.attendance_event
    payment = attendance_event.payment()

    if payment and not event.attendance_event.is_on_waitlist(user):
        if payment.payment_type == 3:
            deadline = timezone.now() + payment.delay
            payment.create_payment_delay(user, deadline)
        else:
            deadline = payment.deadline

        # Send notification about payment to user by mail
        subject = (
            "[%s] Husk å betale for å fullføre påmeldingen til arrangementet."
            % event.title
        )

        content = render_to_string(
            "events/email/payment_reminder.txt",
            {
                "event": event.title,
                "time": deadline.astimezone(tz("Europe/Oslo")).strftime(
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
    send_to_users = _to_email_options[_to_email_value][0]

    signature = f"\n\nVennlig hilsen Linjeforeningen Online.\n(Denne eposten kan besvares til {from_email})"

    message = f"{_message}{signature}"

    # Send mail
    try:
        email_addresses = [a.user.primary_email for a in send_to_users]
        _email_sent = EmailMessage(
            str(subject),
            str(message),
            from_email,
            [from_email],
            email_addresses,
            attachments=(_images),
        ).send()
        logger.info(
            'Sent mail to %s for event "%s".'
            % (_to_email_options[_to_email_value][1], event)
        )
        return _email_sent, all_attendees, attendees_on_waitlist, attendees_not_paid
    except ImproperlyConfigured as e:
        logger.error(
            'Something went wrong while trying to send mail to %s for event "%s"\n%s'
            % (_to_email_options[_to_email_value][1], event, e)
        )
