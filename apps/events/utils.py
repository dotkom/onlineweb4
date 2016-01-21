#-*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from django.core.signing import Signer, BadSignature
from django.http import HttpResponse
from django.utils import timezone
from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event
from apps.payment.models import PaymentDelay
from apps.splash.models import SplashYear

import icalendar


def get_group_restricted_events(user):
    """ Returns a queryset of events with attendance_event that a user has access to """
    types_allowed = []

    groups = user.groups.all()

    if reduce(lambda r, g: g.name in ['Hovedstyret', 'dotKom'] or r, groups, False):
        return Event.objects.filter(attendance_event__isnull=False)

    for group in groups:
        if group.name == 'arrKom':
            types_allowed.append(1) # sosialt
            types_allowed.append(4) # utflukt

        if group.name == 'bedKom':
            types_allowed.append(2) # bedriftspresentasjon

        if group.name == 'fagKom':
            types_allowed.append(3) # kurs

    return Event.objects.filter(attendance_event__isnull=False, event_type__in=types_allowed)


def handle_waitlist_bump(event, host, attendees, payment=None):

    title = u'Du har fått plass på %s' % (event.title)

    extended_deadline = timezone.now() + timedelta(days=2)

    context = {}
    context['title'] = event.title

    if payment:
        context['payment'] = payment
        if payment.payment_type == 1: #Instant
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, extended_deadline)

        elif payment.payment_type == 2: #Deadline
            if extended_deadline > payment.deadline:  # The deadline is in less than 2 days
                for attendee in attendees:
                    payment.create_payment_delay(attendee.user, extended_deadline)

        elif payment.payment_type == 3: #Delay
            deadline = timezone.now() + timedelta(days=payment.delay)
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, deadline)

        if payment.prices():
            context['payment_prices'] = payment.prices()

    context['uri'] = u"http://%(host)s%(abs_url)s" % {'host': host, 'abs_url': event.get_absolute_url()}

    for attendee in attendees:
        context['my_payment'] = None
        try:
            delay = PaymentDelay.objects.get(payment=payment, user=attendee.user)
            delay.deadline = delay.valid_to
            context['my_payment'] = delay
        except PaymentDelay.DoesNotExist:
            context['my_payment'] = context['payment']
        send_mail(title, render_to_string('events/email/waitlist_bump_tpl.txt', context), settings.DEFAULT_FROM_EMAIL, [attendee.user.email])


class Calendar(object):
    def __init__(self):
        self.cal = icalendar.Calendar()
        # Filename served by webserver
        self.filename = 'online'
        # Required ical info
        self.cal.add('prodid', '-//Online//Onlineweb//EN')
        self.cal.add('version', '2.0')

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
        response = HttpResponse(self.cal.to_ical(), content_type='text/calendar')
        response['Content-Type'] = 'text/calendar; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename=' + self.filename + '.ics'
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
            self.add_events(Event.objects.filter(
                attendance_event__attendees__user=user
            ).order_by('event_start').prefetch_related(
                'attendance_event', 'attendance_event__attendees'
            ))
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
        self.add_events(Event.objects.filter(event_end__gt=timezone.now()).order_by('event_start'))
        self.filename = 'events'

    def add_event(self, event):
        cal_event = icalendar.Event()

        cal_event.add('dtstart', event.event_start)
        cal_event.add('dtend', event.event_end)
        cal_event.add('location', event.location)
        cal_event.add('summary', event.title)
        cal_event.add('description', event.ingress_short)
        cal_event.add('uid', 'event-' + str(event.id) + '@online.ntnu.no')

        self.cal.add_component(cal_event)


class SplashCalendar(Calendar):
    def add_event(self, event):
        cal_event = icalendar.Event()
        cal_event.add('dtstart', event.start_time)
        cal_event.add('dtend', event.end_time)
        cal_event.add('summary', event.title)
        cal_event.add('description', event.content)
        cal_event.add('uid', 'splash-' + str(event.id) + '@online.ntnu.no')

        self.cal.add_component(cal_event)

    def events(self):
        self.add_events(SplashYear.objects.current_events())
        self.filename = 'events'


def find_image_versions(event):
    img = event.image
    img_strings = []

    for ver in VERSIONS.keys():
        if ver.startswith('events_'):
            img_strings.append(img.version_generate(ver).url)

    return img_strings
