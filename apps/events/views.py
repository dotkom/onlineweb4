# -*- coding: utf-8 -*-

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
# API v1
from guardian.shortcuts import get_objects_for_user
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from watson import search as watson

from apps.authentication.models import OnlineUser as User
from apps.events.filters import AttendanceEventFilter, EventDateFilter
from apps.events.forms import CaptchaForm
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event
from apps.events.pdf_generator import EventPDF
from apps.events.serializers import (AttendanceEventSerializer,
                                     AttendeeRegistrationCreateSerializer,
                                     AttendeeRegistrationReadOnlySerializer,
                                     AttendeeRegistrationUpdateSerializer, AttendeeSerializer,
                                     CompanyEventSerializer, EventSerializer,
                                     UserAttendanceEventSerializer)
from apps.events.utils import (handle_attend_event_payment, handle_attendance_event_detail,
                               handle_event_ajax, handle_event_payment, handle_mail_participants)
from apps.oidc_provider.authentication import OidcOauth2Auth
from apps.payment.models import Payment, PaymentDelay, PaymentRelation

from .utils import EventCalendar


def index(request):
    context = {}
    if request.user and request.user.is_authenticated:
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

    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST and 'extras_id' in request.POST:
            return JsonResponse(handle_event_ajax(event, request.user,
                                                  request.POST['action'], request.POST['extras_id']))

    form = CaptchaForm(user=request.user)
    context = {
        'captcha_form': form,
        'event': event,
        'ics_path': request.build_absolute_uri(reverse('event_ics', args=(event.id,))),
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
        attendee.show_as_attending_event = request.user.get_visible_as_attending_events()
        attendee.save()
        messages.success(request, _("Du er nå meldt på arrangementet."))

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

    if request.user.has_perm('events.change_event', obj=event):
        return EventPDF(event).render_pdf()

    messages.error(request, _('Du har ikke tilgang til listen for dette arrangementet.'))
    return redirect(event)


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='Komiteer').count() == 1)
def generate_json(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # If this is not an attendance event, redirect to event with error
    if not event.attendance_event:
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if not request.user.has_perm('events.change_event', obj=event):
        messages.error(request, _('Du har ikke tilgang til listen for dette arrangementet.'))
        return redirect(event)

    attendee_unsorted = event.attendance_event.attending_attendees_qs
    attendee_sorted = sorted(attendee_unsorted, key=lambda attendee: attendee.user.last_name)
    waiters = event.attendance_event.waitlist_qs
    reserve = event.attendance_event.reservees_qs
    # Goes though attendance, the waitlist and reservations, and adds them to a json file.
    attendees = []
    for a in attendee_sorted:
        attendees.append({
            "first_name": a.user.first_name,
            "last_name": a.user.last_name,
            "year": a.user.year,
            "phone_number": a.user.phone_number,
            "allergies": a.user.allergies
        })
    waitlist = []
    for w in waiters:
        waitlist.append({
            "first_name": w.user.first_name,
            "last_name": w.user.last_name,
            "year": w.user.year,
            "phone_number": w.user.phone_number
        })

    reservees = []
    for r in reserve:
        reservees.append({
            "name": r.name,
            "note": r.note
        })

    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="' + str(event.id) + '.json"'
    response.write(json.dumps({
        'Attendees': attendees,
        'Waitlist': waitlist,
        'Reservations': reservees
    }))

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
    if not request.user.has_perm('events.change_event', obj=event):
        messages.error(request, _('Du har ikke tilgang til å vise denne siden.'))
        return redirect(event)

    all_attendees = list(event.attendance_event.attending_attendees_qs)
    attendees_on_waitlist = list(event.attendance_event.waitlist_qs)
    attendees_not_paid = list(event.attendance_event.attendees_not_paid)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        images = [(image.name, image.read(), image.content_type) for image in request.FILES.getlist('image')]
        mail_sent = handle_mail_participants(
            event,
            request.POST.get('from_email'),
            request.POST.get('to_email'),
            subject,
            message,
            images,
            all_attendees,
            attendees_on_waitlist,
            attendees_not_paid
        )

        if mail_sent:
            messages.success(request, _('Mailen ble sendt'))
        else:
            messages.error(request, _('Vi klarte ikke å sende mailene dine. Prøv igjen'))

    return render(request, 'events/mail_participants.html', {
        'all_attendees': all_attendees, 'attendees_on_waitlist': attendees_on_waitlist,
        'attendees_not_paid': attendees_not_paid, 'event': event
    })


@login_required
def toggleShowAsAttending(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if not event.is_attendance_event():
        messages.error(request, _("Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    attendance_event = event.attendance_event
    attendee = Attendee.objects.get(event=attendance_event, user=request.user)

    if (attendee.show_as_attending_event):
        attendee.show_as_attending_event = False
        messages.success(request, _("Du er ikke lenger synlig som påmeldt dette arrangementet."))
    else:
        attendee.show_as_attending_event = True
        messages.success(request, _("Du er nå synlig som påmeldt dette arrangementet."))

    attendee.save()
    return redirect(event)


class EventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)
    filterset_class = EventDateFilter
    filterset_fields = ('event_start', 'event_end', 'id',)
    ordering_fields = ('event_start', 'event_end', 'id', 'is_today', 'registration_filtered')
    ordering = ('-is_today', 'registration_filtered', 'id')

    def get_queryset(self):
        """
        :return: Queryset filtered by these requirements:
            event is visible AND (event has NO group restriction OR user having access to restricted event)
        """
        return Event.by_registration.filter(
            (Q(group_restriction__isnull=True) | Q(group_restriction__groups__in=self.request.user.groups.all())) &
            Q(visible=True)). \
            distinct()


class UserAttendanceEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceEvent.objects.all()
    serializer_class = UserAttendanceEventSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = AttendanceEventFilter


class AttendanceEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AttendanceEvent.objects.all()
    serializer_class = AttendanceEventSerializer
    permission_classes = (AllowAny,)


class UserAttendeeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('event', 'attended',)

    def get_queryset(self):
        return Attendee.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AttendeeRegistrationCreateSerializer
        if self.action in ['update', 'partial_update']:
            return AttendeeRegistrationUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return AttendeeRegistrationReadOnlySerializer

        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        attendee = self.get_object()
        attendance_event = attendee.event

        # User can only be unattended before the deadline, or if they are on the wait list.
        if timezone.now() > attendance_event.unattend_deadline and not attendance_event.is_on_waitlist(user):
            return Response({
                'message': 'Avmeldingsfristen har gått ut, det er ikke lenger mulig å melde seg av arrangementet.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if attendance_event.event.event_start < timezone.now():
            return Response({
                'message': 'Du kan ikke melde deg av et arrangement som allerde har startet.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if attendee.has_paid:
            return Response({
                'message': 'Du må refundere betalingene dine før du kan melde deg av.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Attendees un-attend with themselves as the admin user
        attendee.unattend(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class AttendeeViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = AttendeeSerializer
    authentication_classes = [OidcOauth2Auth]
    filterset_fields = ('event', 'attended',)

    @staticmethod
    def _get_allowed_attendees(user):
        if user.is_superuser:
            return Attendee.objects.all()
        allowed_events = get_objects_for_user(
            user,
            'events.change_event',
            accept_global_perms=False
        )
        attendance_events = AttendanceEvent.objects.filter(event__in=allowed_events)
        return Attendee.objects.filter(event__in=attendance_events)

    def get_queryset(self):
        return self._get_allowed_attendees(self.request.user)


class CompanyEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = CompanyEvent.objects.all()
    serializer_class = CompanyEventSerializer
    permission_classes = (AllowAny,)


class AttendViewSet(views.APIView):
    authentication_classes = [OidcOauth2Auth]

    @staticmethod
    def _validate_attend_params(rfid, username):
        logger = logging.getLogger(__name__)

        if not (username or rfid):
            return {
                'message': 'Mangler både RFID og brukernavn. Vennligst prøv igjen.',
                'attend_status': 41,
            }

        # If attendee has typed in username to bind a new card to their user
        if username is not None and rfid is not None:
            try:
                user = User.objects.get(username=username)
                user.rfid = rfid
                user.save()
                logger.debug('Storing new RFID to user "%s"' % user, extra={
                    'user': user.pk,
                    'rfid': rfid,
                })
            except User.DoesNotExist:
                return {
                    'message': 'Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! '
                               '(Prøv igjen, eller scan nytt kort for å avbryte.)',
                    'attend_status': 50,
                }
            except (IntegrityError, ValidationError):
                logger.error('Could not store RFID information for username "{}" with RFID "{}".'.format(
                    username, rfid,
                ))
                return {
                    'message': 'Det oppstod en feil da vi prøvde å lagre informasjonen. Vennligst prøv igjen. '
                               'Dersom problemet vedvarer, ta kontakt med dotkom. '
                               'Personen kan registreres med brukernavn i steden for RFID.',
                    'attend_status': 51,
                }

        return {}

    @staticmethod
    def _authorize_user(user, event_id):
        try:
            if not user.is_authenticated:
                return Response({
                    'message': 'Administerende bruker må være logget inn for å registrere oppmøte',
                    'attend_status': 60
                    }, status=status.HTTP_401_UNAUTHORIZED)

            if not event_id:
                return Response({
                    'message': 'Arrangementets id er ikke oppgitt',
                    'attend_status': 42
                    }, status=status.HTTP_400_BAD_REQUEST)

            event_object = Event.objects.get(pk=event_id)
            if not user.has_perm('events.change_event', event_object):
                return Response({
                    'message': 'Administerende bruker har ikke rettigheter til å registrere oppmøte '
                               'på dette arrangementet',
                    'attend_status': 61
                    }, status=status.HTTP_403_FORBIDDEN)
        except Event.DoesNotExist:
            return Response({
                'message': 'Det gitte arrangementet eksisterer ikke',
                'attend_status': 62
                }, status=status.HTTP_404_NOT_FOUND)
        return False

    def post(self, request, format=None):
        logger = logging.getLogger(__name__)

        rfid = request.data.get('rfid')
        event = request.data.get('event')
        username = request.data.get('username')
        waitlist_approved = request.data.get('approved')

        auth_error = self._authorize_user(request.user, event)
        if auth_error:
            return auth_error

        error = self._validate_attend_params(rfid, username)
        if 'message' in error and 'attend_status' in error:
            return Response({'message': error.get('message'), 'attend_status': error.get('attend_status')},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        try:
            # If attendee is trying to attend by username
            if not rfid:
                logger.debug('Retrieving attendee by username', extra={
                    'event': event,
                    'username': username,
                    'rfid': rfid,
                })
                attendee = Attendee.objects.get(event=event, user__username=username)
            else:
                logger.debug('Retrieving attendee by rfid', extra={
                    'event': event,
                    'username': username,
                    'rfid': rfid,
                })
                attendee = Attendee.objects.get(event=event, user__rfid=rfid)

            # If attendee is already marked as attended
            if attendee.attended:
                logger.debug('Attendee already marked as attended.', extra={
                    'user': attendee.user.id,
                    'event': event,
                })
                return Response({'message': (attendee.user.get_full_name() +
                                             ' har allerede registrert oppmøte.'), 'attend_status': 20},
                                status=status.HTTP_400_BAD_REQUEST)

            # If attendee is on waitlist (bypassed if attendee has gotten the all-clear)
            if attendee.is_on_waitlist() and not waitlist_approved:
                return Response({'message': (attendee.user.get_full_name() +
                                             ' er på venteliste. Registrer dem som møtt opp allikevel?'),
                                 'attend_status': 30},
                                status=status.HTTP_403_FORBIDDEN)

            # All is clear, set attendee to attended and save
            attendee.attended = True
            attendee.save()

        except Attendee.DoesNotExist:

            # If attendee tried to attend by a username that isn't tied to a user
            if rfid is None:
                return Response({'message': 'Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! '
                                            '(Prøv igjen, eller scan nytt kort for å avbryte.)', 'attend_status': 50},
                                status=status.HTTP_400_BAD_REQUEST)

            # If attendee tried to attend by card, but card isn't tied to a user
            else:
                return Response({'message': 'Kortet finnes ikke i databasen. '
                                            'Skriv inn et online.ntnu.no brukernavn for å '
                                            'knytte kortet til brukeren og registrere oppmøte.',
                                 'attend_status': 40}, status=status.HTTP_400_BAD_REQUEST)

        # All is clear, attendee is attended
        return Response({'message': (attendee.user.get_full_name() + ' er registrert som deltaker. Velkommen!'),
                         'attend_status': 10, 'attendee': attendee.id}, status=status.HTTP_200_OK)
