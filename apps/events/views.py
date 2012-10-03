#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from onlineweb4.apps.events import Event

def single(request, event_id):
    event = Event.object.filter(id=event_id)
    #TODO handle event_id outofbounds.
    return render_to_response('events/single.html', {'event' : event})
