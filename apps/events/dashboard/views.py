# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DeleteView, UpdateView
from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user

from apps.dashboard.tools import (
    DashboardCreatePermissionMixin,
    DashboardObjectPermissionMixin,
    DashboardPermissionMixin,
    get_base_context,
    has_access,
)
from apps.events.dashboard import forms as dashboard_forms
from apps.events.dashboard.utils import event_ajax_handler
from apps.events.models import (
    AttendanceEvent,
    Attendee,
    CompanyEvent,
    Event,
    Reservation,
    Reservee,
)
from apps.feedback.models import FeedbackRelation
from apps.payment.models import Payment, PaymentPrice, PaymentRelation


@login_required
@permission_required("events.view_event", return_403=True)
def index(request):
    if not has_access(request):
        raise PermissionDenied

    allowed_events = get_objects_for_user(
        request.user, "events.change_event", accept_global_perms=False
    )
    events = allowed_events.filter(event_start__gte=timezone.now().date()).order_by(
        "event_start"
    )

    context = get_base_context(request)
    context["events"] = events

    return render(request, "events/dashboard/index.html", context)


@login_required
@permission_required("events.view_event", return_403=True)
def past(request):
    if not has_access(request):
        raise PermissionDenied

    allowed_events = get_objects_for_user(
        request.user, "events.change_event", accept_global_perms=False
    )
    events = allowed_events.filter(event_start__lt=timezone.now().date()).order_by(
        "-event_start"
    )

    context = get_base_context(request)
    context["events"] = events

    return render(request, "events/dashboard/index.html", context)


class CreateEventView(DashboardCreatePermissionMixin, CreateView):
    model = Event
    form_class = dashboard_forms.CreateEventForm
    template_name = "events/dashboard/create.html"
    permission_required = "events.add_event"

    def get_success_url(self):
        return reverse("dashboard_event_details", kwargs={"event_id": self.object.id})


class UpdateEventView(DashboardObjectPermissionMixin, UpdateView):
    model = Event
    form_class = dashboard_forms.CreateEventForm
    template_name = "events/dashboard/event_form.html"
    permission_required = "events.change_event"
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class AddAttendanceView(DashboardCreatePermissionMixin, CreateView):
    model = AttendanceEvent
    form_class = dashboard_forms.CreateAttendanceEventForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.add_attendanceevent"
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        form.instance.event = get_object_or_404(Event, pk=self.kwargs.get("event_id"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class UpdateAttendanceView(DashboardObjectPermissionMixin, UpdateView):
    model = AttendanceEvent
    form_class = dashboard_forms.CreateAttendanceEventForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.change_attendanceevent"
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class AddCompanyEventView(DashboardCreatePermissionMixin, CreateView):
    model = CompanyEvent
    form_class = dashboard_forms.AddCompanyForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )

    def form_valid(self, form):
        form.instance.event = get_object_or_404(Event, pk=self.kwargs.get("event_id"))
        return super().form_valid(form)


class RemoveCompanyEventView(DashboardObjectPermissionMixin, DeleteView):
    model = CompanyEvent
    permission_required = "events.add_attendanceevent"
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class AddFeedbackRelationView(DashboardCreatePermissionMixin, CreateView):
    model = FeedbackRelation
    form_class = dashboard_forms.CreateFeedbackRelationForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.content_type = ContentType.objects.get_for_model(Event)
        form.instance.object_id = self.kwargs.get("event_id")
        return super().form_valid(form)


class RemoveFeedbackRelationView(DashboardObjectPermissionMixin, DeleteView):
    model = FeedbackRelation
    permission_required = "events.add_attendanceevent"
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class AddPaymentView(DashboardPermissionMixin, CreateView):
    model = Payment
    form_class = dashboard_forms.CreatePaymentForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )

    def form_valid(self, form):
        form.instance.content_type = ContentType.objects.get_for_model(AttendanceEvent)
        form.instance.object_id = self.kwargs.get("event_id")
        return super().form_valid(form)


class RemovePaymentView(DashboardPermissionMixin, DeleteView):
    model = Payment
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class AddPaymentPriceView(DashboardPermissionMixin, CreateView):
    model = PaymentPrice
    form_class = dashboard_forms.CreatePaymentPriceForm
    template_name = "events/dashboard/attendanceevent_form.html"
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )

    def form_valid(self, form):
        form.instance.payment = get_object_or_404(Payment, pk=self.kwargs.get("pk"))
        return super().form_valid(form)


class RemovePaymentPriceView(DashboardPermissionMixin, DeleteView):
    model = PaymentPrice
    permission_required = "events.add_attendanceevent"

    def get_success_url(self):
        return reverse(
            "dashboard_event_details", kwargs={"event_id": self.kwargs.get("event_id")}
        )


def _create_details_context(request, event_id):
    """
    Prepare a context to be shared for all detail views.
    """

    event = get_object_or_404(Event, pk=event_id)

    # Start with adding base context and the event itself
    context = get_base_context(request)
    context["event"] = event

    # Add forms
    context["change_event_form"] = dashboard_forms.ChangeEventForm(instance=event)
    if event.is_attendance_event():
        context["change_attendance_form"] = dashboard_forms.ChangeAttendanceEventForm(
            instance=event.attendance_event
        )
        if event.attendance_event.has_reservation:
            context["change_reservation_form"] = dashboard_forms.ChangeReservationForm(
                instance=event.attendance_event.reserved_seats
            )
            seats = event.attendance_event.reserved_seats.seats
            ReserveeFormSet = modelformset_factory(
                Reservee,
                max_num=seats,
                extra=seats,
                fields=["name", "note", "allergies"],
            )
            context["change_reservees_formset"] = ReserveeFormSet(
                queryset=event.attendance_event.reserved_seats.reservees.all()
            )

    return context


def _payment_prices(attendance_event):
    payments = {}
    summary = OrderedDict()

    payment = attendance_event.payment()

    if payment and len(payment.prices()) > 1:

        for price in payment.prices():
            summary[price] = 0

        summary["Ikke valgt"] = 0

        for attendee in attendance_event.attending_attendees_qs:
            paymentRelation = PaymentRelation.objects.filter(
                payment=attendance_event.payment(), user=attendee.user, refunded=False
            )

            if paymentRelation:
                payments[attendee] = paymentRelation[0].payment_price
                summary[paymentRelation[0].payment_price] += 1
            else:
                payments[attendee] = "-"
                summary["Ikke valgt"] += 1

    return (payments, summary)


@login_required
@permission_required("events.change_event", return_403=True)
def event_details(request, event_id, active_tab="details"):
    if not has_access(request):
        raise PermissionDenied

    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm("events.change_event", obj=event):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    event = context["event"]
    context["active_tab"] = active_tab
    context["form"] = dashboard_forms.CreateEventForm(instance=event)

    extras = {}
    if event.is_attendance_event() and event.attendance_event.extras:
        for extra in event.attendance_event.extras.all():
            extras[extra] = {"type": extra, "attending": 0, "waits": 0, "allergics": []}

        count_extras(extras, "attending", event.attendance_event.attending_attendees_qs)
        count_extras(extras, "waits", event.attendance_event.waitlist_qs)

    context["extras"] = extras

    return render(request, "events/dashboard/details.html", context)


@login_required
@permission_required("events.view_attendanceevent", return_403=True)
def event_change_attendance(request, event_id):
    context = _create_details_context(request, event_id)
    context["active_tab"] = "attendance"

    event = context["event"]

    if not event.is_attendance_event():
        registration_start = datetime.combine(
            event.event_start - timedelta(days=7), time(12, 0, 0)
        )
        timezone.make_aware(registration_start, timezone.get_current_timezone())
        unattend_deadline = registration_start + timedelta(days=5)
        registration_end = registration_start + timedelta(days=6)

        attendance_event = AttendanceEvent(
            event=event,
            max_capacity=0,
            registration_start=registration_start,
            unattend_deadline=unattend_deadline,
            registration_end=registration_end,
        )
        attendance_event.save()
        context["change_attendance_form"] = dashboard_forms.ChangeAttendanceEventForm(
            instance=event.attendance_event
        )

    else:
        if request.method == "POST":
            form = dashboard_forms.ChangeAttendanceEventForm(
                request.POST, instance=event.attendance_event
            )
            if form.is_valid():
                form.save()
                messages.success(request, _("Påmeldingsdetaljer ble lagret."))
            context["change_attendance_form"] = form

    return render(request, "events/dashboard/details.html", context)


@login_required
@permission_required("events.view_attendee", return_403=True)
def event_change_attendees(request, event_id, active_tab="attendees"):
    if not has_access(request):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    context["active_tab"] = "attendees"

    event = context["event"]

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(
            "dashboard_event_details_active", event_id=event.id, active_tab="details"
        )

    # AJAX
    if request.method == "POST":
        if request.is_ajax and "action" in request.POST:
            if not event.is_attendance_event:
                return HttpResponse(
                    _("Dette er ikke et påmeldingsarrangement."), status=400
                )

            return JsonResponse(event_ajax_handler(event, request))

    # NON AJAX
    context = get_base_context(request)

    context["event"] = event
    context["active_tab"] = active_tab

    extras = {}
    if event.is_attendance_event() and event.attendance_event.extras:
        for extra in event.attendance_event.extras.all():
            extras[extra] = {"type": extra, "attending": 0, "waits": 0, "allergics": []}

        count_extras(extras, "attending", event.attendance_event.attending_attendees_qs)
        count_extras(extras, "waits", event.attendance_event.waitlist_qs)

    context["change_event_form"] = dashboard_forms.ChangeEventForm(instance=event)
    if event.is_attendance_event():
        context["change_attendance_form"] = dashboard_forms.ChangeAttendanceEventForm(
            instance=event.attendance_event
        )
        prices = _payment_prices(event.attendance_event)
        context["payment_prices"] = prices[0]
        context["payment_price_summary"] = prices[1]

    context["extras"] = extras
    context["change_event_form"] = dashboard_forms.ChangeEventForm(instance=event)

    return render(request, "events/dashboard/details.html", context)


def count_extras(event_extras, attendance_list, attendees):
    for attendee in attendees:
        choice = attendee.extras
        if attendee.extras not in event_extras:
            event_extras[choice] = {
                "type": choice,
                "attending": 0,
                "waits": 0,
                "allergics": [],
            }
        ex = event_extras[choice]
        ex[attendance_list] += 1
        if attendee.user.allergies:
            what_list = "påmeldt" if attendance_list == "attending" else "venteliste"
            ex["allergics"].append({"user": attendee.user, "list": what_list})


@login_required
@permission_required("events.view_reservation", return_403=True)
def event_change_reservation(request, event_id):
    if not has_access(request):
        raise PermissionDenied

    context = _create_details_context(request, event_id)
    context["active_tab"] = "reservation"

    event = context["event"]

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(
            "dashboard_event_details_active", event_id=event.id, active_tab="details"
        )

    if request.method == "POST":
        if not event.attendance_event.has_reservation:
            reservation = Reservation(attendance_event=event.attendance_event, seats=0)
            reservation.save()
            context["change_reservation_form"] = dashboard_forms.ChangeReservationForm(
                instance=reservation
            )
        else:
            form = dashboard_forms.ChangeReservationForm(
                request.POST, instance=event.attendance_event.reserved_seats
            )
            if form.is_valid():
                messages.success(request, _("Reservasjonen ble lagret."))
                form.save()
            context["change_reservation_form"] = form

    return render(request, "events/dashboard/details.html", context)


@login_required
@permission_required("events.view_attendee", return_403=True)
def attendee_details(request, attendee_id):

    context = get_base_context(request)

    attendee = get_object_or_404(Attendee, pk=attendee_id)

    context["attendee"] = attendee
    return render(request, "events/dashboard/attendee.html", context)
