#-*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.events.forms import CaptchaForm
import datetime


def index(request):
    events = Event.objects.filter(event_start__gte=datetime.date.today())
    if len(events) == 1:
        return details(request, events[0].id)
    return render(request, 'events/index.html', {'events': events})


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    is_attendance_event = False

    try:
        attendance_event = AttendanceEvent.objects.get(pk=event_id)
        attendance_event.count_attendees = Attendee.objects.filter(event=attendance_event).count()
        is_attendance_event = True

        position_in_wait_list = 0
        event_opens_when = 'never'
        event_open = False
        form = CaptchaForm()

        if request.user.is_authenticated():
            user_status = 'attending' if attendance_event.is_attendee(request.user) else 'not_attending'
            position_in_wait_list = 0 if request.user.id not in event.wait_list else event.wait_list.index(request.user) + 1
        # When rules appear, do magical stuff here
        # if attendance_event.rules.satisfy:
            event_opens_when = 'placeholder'
            event_open = True
        #else
            #event_opens_when = 'never'
        else:
            user_status = 'anonymous_user'

    except AttendanceEvent.DoesNotExist:
        pass

    if is_attendance_event:
        context = {'event': event,
                'attendance_event': attendance_event,
                'user_status': user_status,
                'position_in_wait_list': position_in_wait_list,
                'event_opens_when': event_opens_when,
                'event_open': event_open,
                'captcha_form': form,
        }
        
        return render(request, 'events/details.html', context)
    else:
        return render(request, 'events/details.html', {'event': event})


def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)

@login_required
def attendEvent(request, event_id):

    if not request.POST:
        messages.error(request, 'Vennligst fyll inn formen.')
        return HttpResponseRedirect(reverse(details, args=[event_id]))

    form = CaptchaForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Du klarte ikke captchaen. Er du en bot?')
        return HttpResponseRedirect(reverse(details, args=[event_id]))

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    event = Event.objects.get(pk=event_id)
    attendance_event = event.attendance_event

    user_eligible = event.is_eligible_for_signup(request.user);

    if user_eligible['status']:
        
        Attendee(event=attendance_event, user=request.user).save()
        messages.success(request, "Du er nå påmeldt på arrangmentet!")
        return HttpResponseRedirect(reverse(details, args=[event_id]))
    else:
        messages.error(request, user_eligible['message'])
        return HttpResponseRedirect(reverse(details, args=[event_id]))

@login_required
def unattendEvent(request, event_id):

    event = AttendanceEvent.objects.get(pk=event_id)
    Attendee.objects.get(event=event, user=request.user).delete()

    messages.success(request, "Du ble meldt av eventen!")
    return HttpResponseRedirect(reverse(details, args=[event_id]))

