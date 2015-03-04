# -*- coding: utf-8 -*-

import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from guardian.decorators import permission_required

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import has_access, get_base_context
from apps.events.models import Event, Attendee
from apps.events.dashboard.forms import ChangeEventForm, ChangeAttendanceEventForm


@login_required
@permission_required('event.view_event', raise_403=True)
def index(request):
    events = Event.objects.filter(event_start__gte=timezone.now().date()).order_by('event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)

@login_required
@permission_required('event.view_event', raise_403=True)
def past(request):
    events = Event.objects.filter(event_start__lt=timezone.now().date()).order_by('-event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)

def create_event(request):
    context = get_base_context(request)
    return render(request, 'events/dashboard/details.html', context) 

    

@login_required
@permission_required('event.view_event', raise_403=True)
def details(request, event_id, active_tab='attendees'):
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    event = get_object_or_404(Event, pk = event_id)
    context['event'] = event
    context['active_tab'] = active_tab

    context['change_event_form'] = ChangeEventForm(instance=event)

    # AJAX
    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            resp = {'status': 200}
            if request.POST['action'] == 'attended':
                attendee = get_object_or_404(Attendee, pk = request.POST['attendee_id'])
                attendee.attended = not attendee.attended
                attendee.save()
                return HttpResponse(json.dumps(resp), status=200)
            if request.POST['action'] == 'paid':
                attendee = get_object_or_404(Attendee, pk = request.POST['attendee_id'])
                attendee.paid = not attendee.paid
                attendee.save()
                return HttpResponse(json.dumps(resp), status=200)
            if request.POST['action'] == 'add_attende':
                user = get_object_or_404(User, pk=int(request.POST['user_id']))
                attendee = Attendee(user = user, event = event)
                attendee.save()
                resp['message'] = '%s ble lagt til i %s' % (resp['full_name'], event)
                resp['attendees'] = [{}]
                return HttpResponse(json.dumps(resp), status=200)


    return render(request, 'events/dashboard/details.html', context)

@login_required
@permission_required('event.view_attendee', raise_403=True)
def attendee_details(request, attendee_id):
    attendee = get_object_or_404(Attendee, pk = attendee_id)
    return render(request, 'events/dashboard/attendee.html', {'attendee': attendee})
