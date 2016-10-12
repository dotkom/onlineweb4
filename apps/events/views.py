# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
# API v1
from oauth2_provider.ext.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import mixins, status, views, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from watson import search as watson

from apps.authentication.models import OnlineUser as User
from apps.events.filters import EventDateFilter
from apps.events.forms import CaptchaForm
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event
from apps.events.pdf_generator import EventPDF
from apps.events.serializers import (AttendanceEventSerializer, AttendeeSerializer,
                                     CompanyEventSerializer, EventSerializer)
from apps.events.utils import (get_group_restricted_events, handle_attend_event_payment,
                               handle_attendance_event_detail, handle_event_ajax,
                               handle_event_payment, handle_mail_participants)
from apps.payment.models import Payment, PaymentDelay, PaymentRelation

from .utils import EventCalendar


def index(request):
    context = {}
    if request.user and request.user.is_authenticated():
        signer = Signer()
        context['signer_value'] = signer.sign(request.user.username)
        context['personal_ics_path'] = request.build_absolute_uri(
            reverse('events_personal_ics', args=(context['signer_value'],)))
    return render(request, 'events/index.html', context)


def details(request, event_id, event_slug):
    event = get_object_or_404(Event, pk=event_id)

    # Restricts access to the event if it is group restricted
    if not event.can_display(request.user):
        messages.error(request, "Du har ikke tilgang til dette arrangementet.")
        return index(request)

    user_access_to_event = False
    if request.user:
        if event in get_group_restricted_events(request.user):
            user_access_to_event = True

    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST and 'extras_id' in request.POST:
            return JsonResponse(handle_event_ajax(event, request.user,
                                request.POST['action'], request.POST['extras_id']))

    form = CaptchaForm(user=request.user)
    context = {
        'captcha_form': form,
        'event': event,
        'ics_path': request.build_absolute_uri(reverse('event_ics', args=(event.id,))),
        'user_access_to_event': user_access_to_event,
    }

    if event.is_attendance_event():
        try:
            payment = Payment.objects.get(content_type=ContentType.objects.get_for_model(AttendanceEvent),
                                          object_id=event_id)
        except Payment.DoesNotExist:
            payment = None

        context = handle_attendance_event_detail(event, request.user, context)
        if payment:
            request.session['payment_id'] = payment.id
            context = handle_event_payment(event, request.user, payment, context)

    return render(request, 'events/details.html', context)


def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)


@login_required
def attendEvent(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    if not request.POST:
        messages.error(request, _('Vennligst fyll ut skjemaet.'))
        return redirect(event)

    form = CaptchaForm(request.POST, user=request.user)

    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

        return redirect(event)

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    attendance_event = event.attendance_event

    response = event.attendance_event.is_eligible_for_signup(request.user)

    if response['status']:
        attendee = Attendee(event=attendance_event, user=request.user)
        if 'note' in form.cleaned_data:
            attendee.note = form.cleaned_data['note']
        attendee.save()
        messages.success(request, _("Du er nå påmeldt på arrangementet!"))

        if attendance_event.payment():
            handle_attend_event_payment(event, request.user)

        return redirect(event)
    else:
        messages.error(request, response['message'])
        return redirect(event)


@login_required
def unattendEvent(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    attendance_event = event.attendance_event

    # Check if user is attending
    if len(Attendee.objects.filter(event=attendance_event, user=request.user)) == 0:
        messages.error(request, _("Du er ikke påmeldt dette arrangementet."))
        return redirect(event)

    # Check if the deadline for unattending has passed
    if attendance_event.unattend_deadline < timezone.now() and not attendance_event.is_on_waitlist(request.user):
        messages.error(request, _("Avmeldingsfristen for dette arrangementet har utløpt."))
        return redirect(event)

    if attendance_event.event.event_start < timezone.now():
        messages.error(request, _("Dette arrangementet har allerede startet."))
        return redirect(event)

    try:
        payment = Payment.objects.get(content_type=ContentType.objects.get_for_model(AttendanceEvent),
                                      object_id=event_id)
    except Payment.DoesNotExist:
        payment = None

    # Delete payment delays connected to the user and event
    if payment:

        payments = PaymentRelation.objects.filter(payment=payment, user=request.user, refunded=False)

        # Return if someone is trying to unatend without refunding
        if payments:
            messages.error(request, _('Du har betalt for arrangementet og må refundere før du kan melde deg av'))
            return redirect(event)

        delays = PaymentDelay.objects.filter(payment=payment, user=request.user)
        for delay in delays:
            delay.delete()

    event.attendance_event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=request.user)
    Attendee.objects.get(event=attendance_event, user=request.user).delete()

    messages.success(request, _("Du ble meldt av arrangementet."))
    return redirect(event)


def search_events(request):
    query = request.GET.get('query')
    filters = {
        'future': request.GET.get('future'),
        'myevents': request.GET.get('myevents')
    }
    events = _search_indexed(request, query, filters)

    return render(request, 'events/search.html', {'events': events})


def _search_indexed(request, query, filters):
    results = []
    kwargs = {}
    order_by = 'event_start'

    if filters['future'] == 'true':
        kwargs['event_start__gte'] = timezone.now()
    else:
        # Reverse order when showing all events
        order_by = '-' + order_by

    if filters['myevents'] == 'true':
        kwargs['attendance_event__attendees__user'] = request.user

    events = Event.objects.filter(**kwargs).order_by(order_by).prefetch_related(
        'attendance_event', 'attendance_event__attendees', 'attendance_event__reserved_seats',
        'attendance_event__reserved_seats__reservees')

    # Filters events that are restricted
    display_events = set()

    for event in events:
        if event.can_display(request.user):
            display_events.add(event.pk)

    events = events.filter(pk__in=display_events)

    if query:
        for result in watson.search(query, models=(events,)):
            results.append(result.object)
        return results[:10]

    return events


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='Komiteer').count() == 1)
def generate_pdf(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    # If this is not an attendance event, redirect to event with error
    if not event.attendance_event:
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if event not in get_group_restricted_events(request.user):
        messages.error(request, _('Du har ikke tilgang til listen for dette arrangementet.'))
        return redirect(event)

    return EventPDF(event).render_pdf()


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
    if not event.attendance_event:
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if event not in get_group_restricted_events(request.user):
        messages.error(request, _('Du har ikke tilgang til å vise denne siden.'))
        return redirect(event)

    all_attendees = list(event.attendance_event.attendees_qs)
    attendees_on_waitlist = list(event.attendance_event.waitlist_qs)
    attendees_not_paid = list(event.attendance_event.attendees_not_paid)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        mail_sent = handle_mail_participants(event, request.POST.get('from_email'), request.POST.get('to_email'),
                                             subject, message, all_attendees, attendees_on_waitlist, attendees_not_paid)

        if mail_sent:
            messages.success(request, _('Mailen ble sendt'))
        else:
            messages.error(request, _('Vi klarte ikke å sende mailene dine. Prøv igjen'))

    return render(request, 'events/mail_participants.html', {
        'all_attendees': all_attendees, 'attendees_on_waitlist': attendees_on_waitlist,
        'attendees_not_paid': attendees_not_paid, 'event': event
    })


class EventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)
    filter_class = EventDateFilter
    filter_fields = ('event_start', 'event_end', 'id',)
    ordering_fields = ('event_start', 'event_end', 'id', 'is_today', 'registration_filtered')
    ordering = ('-is_today', 'registration_filtered', 'id')

    def get_queryset(self):
        """
        :return: Queryset filtered by these requirements:
        - event has NO group restriction OR user having access to restricted event
        """
        return Event.by_registration.filter(
            Q(group_restriction__isnull=True) | Q(group_restriction__groups__in=self.request.user.groups.all())).\
            distinct()


class AttendanceEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AttendanceEvent.objects.all()
    serializer_class = AttendanceEventSerializer
    permission_classes = (AllowAny,)


class AttendeeViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Attendee.objects.all()
    serializer_class = AttendeeSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['regme.readwrite']
    filter_fields = ('event', 'attended',)


class CompanyEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = CompanyEvent.objects.all()
    serializer_class = CompanyEventSerializer
    permission_classes = (AllowAny,)


class AttendViewSet(views.APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['regme.readwrite']

    def post(self, request, format=None):

        rfid = request.data.get('rfid')
        event = request.data.get('event')
        username = request.data.get('username')
        waitlist_approved = request.data.get('approved')
        attendee = None

        if username is not None:
            try:
                user = User.objects.get(username=username)
                user.rfid = rfid
                user.save()
            except User.DoesNotExist:
                return Response({'message': 'Brukernavn finnes ikke. Husk at det er brukernavn på Onlineweb! '
                                            '(Prøv igjen, eller scan nytt kort for å avbryte.)', 'attend_status': 50},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            attendee = Attendee.objects.get(event=event, user__rfid=rfid)
            if attendee.attended:
                return Response({'message': 'Du har allerede møtt opp.', 'attend_status': 20},
                                status=status.HTTP_400_BAD_REQUEST)
            if attendee.is_on_waitlist() and not waitlist_approved:
                return Response({'message': (attendee.user.get_full_name(),
                                             'er på venteliste. Registrere allikevel?'), 'attend_status': 30},
                                status=status.HTTP_100_CONTINUE)
            attendee.attended = True
            attendee.save()
        except Attendee.DoesNotExist:
            return Response({'message': 'Kortet finnes ikke i databasen. '
                                        'Skriv inn et brukernavn for å knytte kortet til brukeren og sjekk inn.',
                             'attend_status': 40}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': (attendee.user.get_full_name(), 'er registrert som deltaker. Velkommen!'),
                         'attend_status': 10}, status=status.HTTP_200_OK)
