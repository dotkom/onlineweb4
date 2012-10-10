#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from events import Event, Attendee
import datetime

def index(request):
    events = Event.objects.filter(start_date__gte=datetime.date.today())
    if len(events) == 1:
        return detauls(request, events[0].id)
    return render_to_response('events/index.html', {'events': events}, contex_instance=RequestContext(request))

def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    return render_to_response('events/details.html', {'event': event}, context_instance=RequestContext(request))

def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)
