# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
from guardian.decorators import permission_required

from apps.dashboard.tools import get_base_context, has_access
from apps.events.dashboard.forms import (ChangeAttendanceEventForm, ChangeEventForm,
                                         ChangeReservationForm)
from apps.events.dashboard.utils import event_ajax_handler
from apps.events.models import AttendanceEvent, Attendee, Event, Reservation, Reservee
from apps.events.utils import get_group_restricted_events, get_types_allowed


@login_required
@permission_required('events.view_event', return_403=True)
def index(request):
    if not has_access(request):
        raise PermissionDenied

    allowed_events = get_group_restricted_events(request.user, True)
    events = allowed_events.filter(event_start__gte=timezone.now().date()).order_by('event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)


@login_required
@permission_required('events.view_event', return_403=True)
def past(request):
    if not has_access(request):
        raise PermissionDenied

    allowed_events = get_group_restricted_events(request.user, True)
    events = allowed_events.filter(event_start__lt=timezone.now().date()).order_by('-event_start')

    context = get_base_context(request)
    context['events'] = events

    return render(request, 'events/dashboard/index.html', context)


@login_required
@permission_required('events.view_event', return_403=True)
def create_event(request):
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    if request.method == 'POST':
        form = ChangeEventForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            if cleaned['event_type'] not in get_types_allowed(request.user):
                messages.error(request, _(
                    "Du har ikke tilgang til å lage arranngement av typen '%s'.") % cleaned['event_type'])
                context['change_event_form'] = form

            else:
                # Create object, but do not commit to db. We need to add stuff.
                event = form.save(commit=False)
                # Add author
                event.author = request.user
                event.save()

                messages.success(request, _("Arrangementet ble opprettet."))
                return redirect('dashboard_event_details', event_id=event.id)

        else:
            context['change_event_form'] = form

    if 'change_event_form' not in context.keys():
        context['change_event_form'] = ChangeEventForm()

    context['event'] = _('Nytt arrangement')
    context['active_tab'] = 'details'

    return render(request, 'events/dashboard/details.html', context)


def _create_details_context(request, event_id):
    """
    Prepare a context to be shared for all detail views.
    """

    event = get_object_or_404(Event, pk=event_id)

    # Start with adding base context and the event itself
    context = get_base_context(request)
    context['event'] = event

    # Add forms
    context['change_event_form'] = ChangeEventForm(instance=event)
    if event.is_attendance_event():
        context['change_attendance_form'] = ChangeAttendanceEventForm(instance=event.attendance_event)
        if event.attendance_event.has_reservation:
            context['change_reservation_form'] = ChangeReservationForm(instance=event.attendance_event.reserved_seats)
            seats = event.attendance_event.reserved_seats.seats
            ReserveeFormSet = modelformset_factory(
                Reservee, max_num=seats, extra=seats, fields=['name', 'note', 'allergies'])
            context['change_reservees_formset'] = ReserveeFormSet(
                queryset=event.attendance_event.reserved_seats.reservees.all())

    return context


@login_required
@permission_required('events.view_event', return_403=True)
def event_details(request, event_id, active_tab='details'):
    if not has_access(request):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    context['active_tab'] = active_tab

    return render(request, 'events/dashboard/details.html', context)


@login_required
@permission_required('events.view_attendanceevent', return_403=True)
def event_change_attendance(request, event_id):
    context = _create_details_context(request, event_id)
    context['active_tab'] = 'attendance'

    event = context['event']

    if not event.is_attendance_event():
        registration_start = datetime.combine(event.event_start - timedelta(days=7), time(12, 0, 0))
        timezone.make_aware(registration_start, timezone.get_current_timezone())
        unattend_deadline = registration_start + timedelta(days=5)
        registration_end = registration_start + timedelta(days=6)

        attendance_event = AttendanceEvent(
            event=event,
            max_capacity=0,
            registration_start=registration_start,
            unattend_deadline=unattend_deadline,
            registration_end=registration_end
        )
        attendance_event.save()
        context['change_attendance_form'] = ChangeAttendanceEventForm(instance=event.attendance_event)

    else:
        if request.method == 'POST':
            form = ChangeAttendanceEventForm(request.POST, instance=event.attendance_event)
            if form.is_valid():
                form.save()
                messages.success(request, _("Påmeldingsdetaljer ble lagret."))
            context['change_attendance_form'] = form

    return render(request, 'events/dashboard/details.html', context)


@login_required
@permission_required('events.view_attendee', return_403=True)
def event_change_attendees(request, event_id, active_tab='attendees'):
    if not has_access(request):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    context['active_tab'] = 'attendees'

    event = context['event']

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect('dashboard_event_details_active', event_id=event.id, active_tab='details')

    # AJAX
    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            if not event.is_attendance_event:
                return HttpResponse(_('Dette er ikke et påmeldingsarrangement.'), status=400)

            return JsonResponse(event_ajax_handler(event, request))

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
            what_list = "påmeldt" if inlist is "attending" else "venteliste"
            ex["allergics"].append({"user": att.user, "list": what_list})


@login_required
@permission_required('events.view_reservation', return_403=True)
def event_change_reservation(request, event_id):
    if not has_access(request):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    context['active_tab'] = 'reservation'

    event = context['event']

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect('dashboard_event_details_active', event_id=event.id, active_tab='details')

    if request.method == 'POST':
        if not event.attendance_event.has_reservation:
            reservation = Reservation(
                attendance_event=event.attendance_event,
                seats=0
            )
            reservation.save()
            context['change_reservation_form'] = ChangeReservationForm(instance=reservation)
        else:
            form = ChangeReservationForm(request.POST, instance=event.attendance_event.reserved_seats)
            if form.is_valid():
                messages.success(request, _("Reservasjonen ble lagret."))
                form.save()
            context['change_reservation_form'] = form

    return render(request, 'events/dashboard/details.html', context)


@login_required
@permission_required('events.view_attendee', return_403=True)
def attendee_details(request, attendee_id):

    context = get_base_context(request)

    attendee = get_object_or_404(Attendee, pk=attendee_id)

    context['attendee'] = attendee
    return render(request, 'events/dashboard/attendee.html', context)
