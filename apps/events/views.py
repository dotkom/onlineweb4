#-*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from apps.events.models import Event, AttendanceEvent, Attendee
import datetime


def index(request):
    events = Event.objects.filter(event_start__gte=datetime.date.today())
    if len(events) == 1:
        return details(request, events[0].id)
    return render_to_response('events/index.html', {'events': events}, context_instance=RequestContext(request))


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    is_attendance_event = False

    try:
        attendance_event = AttendanceEvent.objects.get(pk=event_id)
        attendance_event.count_attendees = Attendee.objects.filter(event=attendance_event).count()
        is_attendance_event = True

        # When rules appear, do magical stuff here
        canAttendWhen = 'never'

    # if attendance_event.rules.satisfy:
        canAttendWhen = 'placeholder'


    except AttendanceEvent.DoesNotExist:
        pass

    if is_attendance_event:
        return render_to_response('events/details.html',
                                  {'event': event,
                                   'attendance_event': attendance_event,
                                   'canAttendWhen': canAttendWhen,
                                  },
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('events/details.html', {'event': event}, context_instance=RequestContext(request))


def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)

@login_required
def attendEvent(request, event_id):

    #Do rules check here as well to prevent scripts

    messages.success(request, "Success!")
    return HttpResponseRedirect(reverse(details, args=[event_id]))

