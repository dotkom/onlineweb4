#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from apps.events.models import Event, AttendanceEvent, Attendee
import datetime


def index(request):
    events = Event.objects.filter(event_start__gte=datetime.date.today())
    if len(events) == 1:
        return details(request, events[0].event_id)
    return render_to_response('events/index.html', {'events': events}, context_instance=RequestContext(request))


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    is_attendance_event = False

    try:
        attendance_event = AttendanceEvent.objects.get(pk=event_id)
        is_attendance_event = True
    except AttendanceEvent.DoesNotExist:
        pass

    if is_attendance_event:
        return render_to_response('events/details.html', {'event': event, 'attendance_event': attendance_event}, context_instance=RequestContext(request))
    else:
        return render_to_response('events/details.html', {'event': event}, context_instance=RequestContext(request))


def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)
