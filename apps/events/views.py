import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.events.models import Event
from apps.events.pdf_generator import EventPDF
from apps.events.utils import (
    handle_mail_participants,
)

from .utils import EventCalendar


@login_required()
def generate_pdf(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # If this is not an attendance event, redirect to event with error
    if not event.attendance_event:
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    if request.user.has_perm("events.change_event", obj=event):
        return EventPDF(event).render_pdf()

    messages.error(
        request, _("Du har ikke tilgang til listen for dette arrangementet.")
    )
    return redirect(event)


@login_required()
def generate_json(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # If this is not an attendance event, redirect to event with error
    if not event.attendance_event:
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if not request.user.has_perm("events.change_event", obj=event):
        messages.error(
            request, _("Du har ikke tilgang til listen for dette arrangementet.")
        )
        return redirect(event)

    attendee_unsorted = event.attendance_event.attending_attendees_qs
    attendee_sorted = sorted(
        attendee_unsorted, key=lambda attendee: attendee.user.last_name
    )
    waiters = event.attendance_event.waitlist_qs
    reserve = event.attendance_event.reservees_qs
    # Goes though attendance, the waitlist and reservations, and adds them to a json file.
    attendees = [
        {
            "first_name": a.user.first_name,
            "last_name": a.user.last_name,
            "year": a.user.year,
            "email": a.user.email,
            "phone_number": a.user.phone_number,
            "allergies": a.user.allergies,
        }
        for a in attendee_sorted
    ]

    waitlist = [
        {
            "first_name": w.user.first_name,
            "last_name": w.user.last_name,
            "year": w.user.year,
            "phone_number": w.user.phone_number,
        }
        for w in waiters
    ]

    reservees = [{"name": r.name, "note": r.note} for r in reserve]

    response = HttpResponse(content_type="application/json")
    response["Content-Disposition"] = (
        'attachment; filename="' + str(event.id) + '.json"'
    )
    response.write(
        json.dumps(
            {"Attendees": attendees, "Waitlist": waitlist, "Reservations": reservees}
        )
    )

    return response


def calendar_export(request, event_id=None, user=None):
    calendar = EventCalendar()
    if event_id:
        # Single event
        calendar.event(event_id)
    elif user:
        # Personalized calendar
        calendar.user(user)
    else:
        # All events that haven't ended yet
        calendar.events()
    return calendar.response()


@login_required
def mail_participants(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # If this is not an attendance event, redirect to event with error
    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if not request.user.has_perm("events.change_event", obj=event):
        messages.error(request, _("Du har ikke tilgang til å vise denne siden."))
        return redirect(event)

    all_attendees = list(event.attendance_event.attending_attendees_qs)
    attendees_on_waitlist = list(event.attendance_event.waitlist_qs)
    attendees_not_paid = list(event.attendance_event.attendees_not_paid)

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        images = [
            (image.name, image.read(), image.content_type)
            for image in request.FILES.getlist("image")
        ]
        mail_sent = handle_mail_participants(
            event,
            request.POST.get("to_email"),
            subject,
            message,
            images,
            all_attendees,
            attendees_on_waitlist,
            attendees_not_paid,
        )

        if mail_sent:
            messages.success(request, _("Mailen ble sendt"))
        else:
            messages.error(
                request, _("Vi klarte ikke å sende mailene dine. Prøv igjen")
            )

    return render(
        request,
        "events/mail_participants.html",
        {
            "all_attendees": all_attendees,
            "attendees_on_waitlist": attendees_on_waitlist,
            "attendees_not_paid": attendees_not_paid,
            "event": event,
        },
    )
