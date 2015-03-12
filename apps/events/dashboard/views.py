# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
import json

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import ugettext as _

from guardian.decorators import permission_required

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import has_access, get_base_context
from apps.events.dashboard.forms import ChangeEventForm, ChangeAttendanceEventForm
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.events.utils import get_group_restricted_events, get_types_allowed


@login_required
@permission_required('events.view_event', return_403=True)
def index(request):
    allowed_events = get_group_restricted_events(request.user, True)
    events = allowed_events.filter(event_start__gte=timezone.now().date()).order_by('event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)

@login_required
@permission_required('events.view_event', return_403=True)
def past(request):
    allowed_events = get_group_restricted_events(request.user, True)
    events = allowed_events.filter(event_start__lt=timezone.now().date()).order_by('-event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)

@login_required
@permission_required('events.view_event', raise_403=True)
def create_event(request):
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    if request.method == 'POST':
        form = ChangeEventForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            if cleaned['event_type'] not in get_types_allowed(request.user):
                messages.error(request, _(u"Du har ikke tilgang til å lage arranngement av typen '%s'.") % cleaned['event_type'])
                context['change_event_form'] = form

            else:
                # Create object, but do not commit to db. We need to add stuff.
                event = form.save(commit=False)
                # Add author
                if not event.author:
                    event.author = request.user
                # Now save it
                event.save()

                messages.success(request, _(u"Arrangementet ble opprettet."))
                return redirect('dashboard_event_details', event_id=event.id)

        else:
            context['change_event_form'] = form


    if 'change_event_form' not in context.keys():
        context['change_event_form'] = ChangeEventForm()

    context['event'] = _('Nytt arrangement')
    context['active_tab'] = 'details'

    return render(request, 'events/dashboard/details.html', context) 


@login_required
@permission_required('events.view_event', raise_403=True)
def event_details(request, event_id, active_tab='details'):
    if not has_access(request):
        raise PermissionDenied

    print "here"

    event = get_object_or_404(Event, pk = event_id)

    # AJAX
    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            resp = {}
            if request.POST['action'] == 'attended':
                if not event.is_attendance_event:
                    return HttpResponse(_(u'Dette er ikke et påmeldingsarrangement.'), status=400)
                attendee = Attendee.objects.filter(pk = request.POST['attendee_id'])
                if attendee.count() != 1:
                    return HttpResponse(_(u'Fant ingen påmeldte med oppgitt ID (%s).') % request.POST['attendee_id'], status=400)
                attendee = attendee[0]
                attendee.attended = not attendee.attended
                attendee.save()
                return JsonResponse(resp)
            if request.POST['action'] == 'paid':
                if not event.is_attendance_event:
                    return HttpResponse(_(u'Dette er ikke et påmeldingsarrangement.'), status=400)
                attendee = Attendee.objects.filter(pk = request.POST['attendee_id'])
                if attendee.count() != 1:
                    return HttpResponse(_(u'Fant ingen påmeldte med oppgitt ID (%s).') % request.POST['attendee_id'], status=400)
                attendee = attendee[0]
                attendee.paid = not attendee.paid
                attendee.save()
                return JsonResponse(resp)
            if request.POST['action'] == 'add_attendee':
                if not event.is_attendance_event:
                    return HttpResponse(_(u'Dette er ikke et påmeldingsarrangement.'), status=400)
                user = User.objects.filter(pk = request.POST['user_id'])
                if user.count() != 1:
                    return HttpResponse(_(u'Fant ingen bruker med oppgitt ID (%s).') % request.POST['user_id'], status=400)
                user = user[0] 
                if Attendee.objects.filter(user=user).count() != 0:
                    return HttpResponse(_(u'%s er allerede påmeldt %s.') % (user.get_full_name(), event.title), status=400)
                attendee = Attendee(user = user, event = event.attendance_event)
                attendee.save()
                resp['message'] = _(u'%s ble meldt på %s') % (user.get_full_name(), event)
                resp['attendees'] = []
                for number, a in enumerate(attendee.event.attendees_qs):
                    resp['attendees'].append({
                        'number': number+1,
                        'id': a.id,
                        'first_name': a.user.first_name,
                        'last_name': a.user.last_name,
                        'paid': a.paid,
                        'extras': str(a.extras),
                        'attended': a.attended,
                        'link': reverse('dashboard_attendee_details', kwargs={'attendee_id': a.id})
                    })
                resp['waitlist'] = []
                for number, a in enumerate(attendee.event.waitlist_qs):
                    resp['waitlist'].append({
                        'number': number+1,
                        'id': a.id,
                        'first_name': a.user.first_name,
                        'last_name': a.user.last_name,
                        'paid': a.paid,
                        'extras': str(a.extras),
                        'attended': a.attended,
                        'link': reverse('dashboard_attendee_details', kwargs={'attendee_id': a.id})
                    })
                return JsonResponse(resp, safe=False)
            if request.POST['action'] == 'remove_attendee':
                if not event.is_attendance_event:
                    return HttpResponse(_(u'Dette er ikke et påmeldingsarrangement.'), status=400)
                attendee = Attendee.objects.filter(pk = request.POST['attendee_id'])
                if attendee.count() != 1:
                    return HttpResponse(_(u'Fant ingen påmeldte med oppgitt ID (%s).') % request.POST['attendee_id'], status=400)
                attendee = attendee[0]
                event.attendance_event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=attendee.user)
                attendee.delete()
                resp['message'] = _(u'%s ble fjernet fra %s') % (attendee.user.get_full_name(), attendee.event)
                resp['attendees'] = []
                for number, a in enumerate(attendee.event.attendees_qs):
                    resp['attendees'].append({
                        'number': number+1,
                        'id': a.id,
                        'first_name': a.user.first_name,
                        'last_name': a.user.last_name,
                        'paid': a.paid,
                        'extras': str(a.extras),
                        'attended': a.attended,
                        'link': reverse('dashboard_attendee_details', kwargs={'attendee_id': a.id})
                    })
                resp['waitlist'] = []
                for number, a in enumerate(attendee.event.waitlist_qs):
                    resp['waitlist'].append({
                        'number': number+1,
                        'id': a.id,
                        'first_name': a.user.first_name,
                        'last_name': a.user.last_name,
                        'paid': a.paid,
                        'extras': str(a.extras),
                        'attended': a.attended,
                        'link': reverse('dashboard_attendee_details', kwargs={'attendee_id': a.id})
                    })
                return JsonResponse(resp)


    # NON AJAX
    context = get_base_context(request)

    context['event'] = event
    context['active_tab'] = active_tab

    extras = {}
    if event.is_attendance_event() and event.attendance_event.extras:
        for extra in event.attendance_event.extras.all():
            extras[extra] = {"type": extra, "attending": 0, "waits": 0, "allergics": []}

        count_extras(extras, "attending", event.attendance_event.attendees_qs)
        count_extras(extras, "waits", event.attendance_event.waitlist_qs)

    context['change_event_form'] = ChangeEventForm(instance=event)
    if event.is_attendance_event():
        context['change_attendance_form'] = ChangeAttendanceEventForm(instance=event.attendance_event)

    context['extras'] = extras
    context['change_event_form'] = ChangeEventForm(instance=event)

    return render(request, 'events/dashboard/details.html', context)


def count_extras(arr, inlist, atts):
    for att in atts:
        choice = "Ikke valgt" if att.extras is None else att.extras
        if att.extras not in arr:
            arr[choice] = {"type": choice, "attending": 0, "waits": 0, "allergics": []}
        ex = arr[choice]
        ex[inlist] += 1
        if att.user.allergies:
            whatList = "påmeldt" if inlist is "attending" else "venteliste"
            ex["allergics"].append({"user": att.user, "list": whatList})


@login_required
@permission_required('events.view_attendanceevent', raise_403=True)
def event_change_attendance(request, event_id):
    event = get_object_or_404(Event, pk = event_id)

    if not event.is_attendance_event():
        registration_start = datetime.combine(event.event_start - timedelta(days=7), time(12, 0, 0))
        timezone.make_aware(registration_start, timezone.get_current_timezone())
        unattend_deadline = registration_start + timedelta(days=5)
        registration_end = registration_start + timedelta(days=6)
        print registration_start

        attendance_event = AttendanceEvent(
            event = event,
            max_capacity = 0,
            registration_start = registration_start,
            unattend_deadline = unattend_deadline,
            registration_end = registration_end
        )
        attendance_event.save()
        return redirect('dashboard_event_details_active', event_id=event.id, active_tab='attendance')

    else:
        if request.method == 'POST':
            form = ChangeAttendanceEventForm(request.POST)
            if form.is_valid():
                attendance_event = form.save(commit=False)
                attendance_event.event = event
                attendance_event.save()

    return redirect('dashboard_event_details_active', event_id=event.id, active_tab='attendance')


@login_required
@permission_required('events.view_attendee', return_403=True)
def attendee_details(request, attendee_id):

    context = get_base_context(request)

    attendee = get_object_or_404(Attendee, pk = attendee_id)

    context['attendee'] = attendee
    return render(request, 'events/dashboard/attendee.html', context)

