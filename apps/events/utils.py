from django.core.signing import Signer, BadSignature
from django.http import HttpResponse
from django.utils import timezone

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event
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
        self.add_events(SplashYear.objects.current().splash_events.all())
        self.filename = 'events'
