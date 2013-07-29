#-*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
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
    user_anonymous = True
    user_attending = False
    place_on_wait_list = 0
    will_be_on_wait_list = False
    rules = []
    user_status = False

    try:
        attendance_event = AttendanceEvent.objects.get(pk=event_id)
        is_attendance_event = True
        form = CaptchaForm()

        if attendance_event.rule_bundles:
            for rule_bundle in attendance_event.rule_bundles.all():
                rules.append(rule_bundle.get_rule_strings)

        if request.user.is_authenticated():
            user_anonymous = False
            if attendance_event.is_attendee(request.user):
                user_attending = True

            if attendance_event.will_i_be_on_wait_list:
                will_be_on_wait_list = True

            user_status = event.is_eligible_for_signup(request.user)

            # Check if this user is on the waitlist
            place_on_wait_list = event.what_place_is_user_on_wait_list(request.user)

    except AttendanceEvent.DoesNotExist:
        pass

    if is_attendance_event:
        context = {
                'event': event,
                'attendance_event': attendance_event,
                'user_anonymous': user_anonymous,
                'user_attending': user_attending,
                'will_be_on_wait_list': will_be_on_wait_list,
                'rules': rules,
                'user_status': user_status,
                'place_on_wait_list': int(place_on_wait_list),
                #'position_in_wait_list': position_in_wait_list,
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
        messages.error(request, _(u'Vennligst fyll ut skjemaet.'))
        return HttpResponseRedirect(reverse(details, args=[event_id]))

    form = CaptchaForm(request.POST)

    if not form.is_valid():
        messages.error(request, _(u'Du klarte ikke captcha-en. Er du en bot?'))
        return HttpResponseRedirect(reverse(details, args=[event_id]))

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    event = Event.objects.get(pk=event_id)
    attendance_event = event.attendance_event

    user_eligible = event.is_eligible_for_signup(request.user);

    if user_eligible['status']:   
        Attendee(event=attendance_event, user=request.user).save()
        messages.success(request, _(u"Du er nå påmeldt på arrangementet!"))
        return HttpResponseRedirect(reverse(details, args=[event_id]))
    else:
        messages.error(request, user_eligible['message'])
        return HttpResponseRedirect(reverse(details, args=[event_id]))

@login_required
def unattendEvent(request, event_id):

    event = AttendanceEvent.objects.get(pk=event_id)
    Attendee.objects.get(event=event, user=request.user).delete()

    messages.success(request, _(u"Du ble meldt av arrangementet."))
    return HttpResponseRedirect(reverse(details, args=[event_id]))

