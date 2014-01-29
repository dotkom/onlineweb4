#-*- coding: utf-8 -*-

import datetime

from django.utils import timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _

import watson

from apps.events.forms import CaptchaForm
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.events.pdf_generator import EventPDF


def index(request):
    return render(request, 'events/index.html', {})

def details(request, event_id, event_slug):
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
        form = CaptchaForm(user=request.user)

        if attendance_event.rule_bundles:
            for rule_bundle in attendance_event.rule_bundles.all():
                rules.append(rule_bundle.get_rule_strings)

        if request.user.is_authenticated():
            user_anonymous = False
            if attendance_event.is_attendee(request.user):
                user_attending = True

            
            will_be_on_wait_list = attendance_event.will_i_be_on_wait_list

            user_status = event.is_eligible_for_signup(request.user)

            # Check if this user is on the waitlist
            place_on_wait_list = event.what_place_is_user_on_wait_list(request.user)

    except AttendanceEvent.DoesNotExist:
        pass

    if is_attendance_event:
        context = {
                'now': timezone.now(),
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
    
    event = get_object_or_404(Event, pk=event_id)

    if not request.POST:
        messages.error(request, _(u'Vennligst fyll ut skjemaet.'))
        return redirect(event)
    form = CaptchaForm(request.POST, user=request.user)

    if not form.is_valid():
        if not 'mark_rules' in request.POST and not request.user.mark_rules:
            error_message = u'Du må godta prikkreglene for å melde deg på.'
        else:
            error_message = u'Du klarte ikke captcha-en. Er du en bot?'
        messages.error(request, _(error_message))
        return redirect(event)

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    attendance_event = event.attendance_event

    response = event.is_eligible_for_signup(request.user);

    if response['status']:   
        # First time accepting mark rules
        if 'mark_rules' in form.cleaned_data:
            request.user.mark_rules = True
            request.user.save()
        Attendee(event=attendance_event, user=request.user).save()
        messages.success(request, _(u"Du er nå påmeldt på arrangementet!"))
        return redirect(event)
    else:
        messages.error(request, response['message'])
        return redirect(event)

@login_required
def unattendEvent(request, event_id):

    event = get_object_or_404(Event, pk=event_id)
    attendance_event = event.attendance_event

    # Check if the deadline for unattending has passed
    if attendance_event.unattend_deadline < timezone.now():
        messages.error(request, _(u"Avmeldingsfristen for dette arrangementet har utløpt."))
        return redirect(event)

    event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=request.user)
    Attendee.objects.get(event=attendance_event, user=request.user).delete()

    messages.success(request, _(u"Du ble meldt av arrangementet."))
    return redirect(event)

def search_events(request):
    query = request.GET.get('query')
    filters = {
        'future' : request.GET.get('future'),
        'myevents' : request.GET.get('myevents')
    }
    events = _search_indexed(request, query, filters)

    return render(request, 'events/search.html', {'events': events})


def _search_indexed(request, query, filters):
    results = []
    kwargs = {}

    if filters['future'] == 'true':
        kwargs['event_start__gte'] = timezone.now()

    if filters['myevents'] == 'true':
        kwargs['attendance_event__attendees'] = request.user

    events = Event.objects.filter(**kwargs).order_by('event_start').prefetch_related(
            'attendance_event', 'attendance_event__attendees')

    if query:
        for result in watson.search(query, models=(events,)):
            results.append(result.object)
        return results[:10]

    return events


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='Komiteer').count() == 1)
def generate_pdf(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return EventPDF(event).render_pdf()
