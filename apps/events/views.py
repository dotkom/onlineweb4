#-*- coding: utf-8 -*-

from datetime import datetime, timedelta
from collections import OrderedDict

from django.utils import timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.core.signing import Signer, BadSignature
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

import watson

from apps.authentication.models import OnlineUser as User
from apps.events.forms import CaptchaForm
from apps.events.models import Event, AttendanceEvent, Attendee, CompanyEvent
from apps.events.pdf_generator import EventPDF
from apps.events.utils import get_group_restricted_events
from apps.payment.models import Payment, PaymentRelation, PaymentDelay

from utils import EventCalendar

def index(request):
    context = {}
    if request.user and request.user.is_authenticated():
        signer = Signer()
        context['signer_value'] = signer.sign(request.user.username)
        context['personal_ics_path'] = request.build_absolute_uri(reverse('events_personal_ics', args=(context['signer_value'],)))
    return render(request, 'events/index.html', context)


def details(request, event_id, event_slug):
    event = get_object_or_404(Event, pk=event_id)

    #Restricts access to the event if it is group restricted
    if not event.can_display(request.user):
        messages.error(request, "Du har ikke tilgang til denne eventen.")
        return index(request)

    user_anonymous = True
    user_attending = False
    attendee = False
    place_on_wait_list = 0
    will_be_on_wait_list = False
    rules = []
    user_status = False
    user_paid = False
    payment_delay = False
    payment_relation_id = False

    user_access_to_event = False
    if request.user:
        if event in get_group_restricted_events(request.user):
            user_access_to_event = True

    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            resp = {'message': "Feil!"}
            if request.POST['action'] == 'extras':
                if not event.is_attendance_event:
                    return HttpResponse(u'Dette er ikke et påmeldingsarrangement.', status=400)

                attendance_event = AttendanceEvent.objects.get(pk=event_id)

                if not attendance_event.is_attendee(request.user):
                    return HttpResponse(u'Du er ikke påmeldt dette arrangementet.', status=401)

                attendee = Attendee.objects.get(event=attendance_event, user=request.user)
                attendee.extras = attendance_event.extras.all()[int(request.POST['extras_id'])]
                attendee.save()
                resp['message'] = "Lagret ditt valg"
                return JsonResponse(resp)

    context = {'event': event, 'ics_path': request.build_absolute_uri(reverse('event_ics', args=(event.id,)))}

    if event.is_attendance_event():
        attendance_event = AttendanceEvent.objects.get(pk=event_id)
        form = CaptchaForm(user=request.user)

        if attendance_event.rule_bundles:
            for rule_bundle in attendance_event.rule_bundles.all():
                rules.append(rule_bundle.get_rule_strings)

        if request.user.is_authenticated():
            user_anonymous = False
            if attendance_event.is_attendee(request.user):
                user_attending = True
                attendee = Attendee.objects.get(event=attendance_event, user=request.user)



            will_be_on_wait_list = attendance_event.will_i_be_on_wait_list

            user_status = event.attendance_event.is_eligible_for_signup(request.user)

            # Check if this user is on the waitlist
            place_on_wait_list = attendance_event.what_place_is_user_on_wait_list(request.user)

        try:
            payment = Payment.objects.get(content_type=ContentType.objects.get_for_model(AttendanceEvent),
                object_id=event_id)
        except Payment.DoesNotExist:
            payment = None

        if payment:
            request.session['payment_id'] = payment.id

            if not user_anonymous:
                payment_relations = PaymentRelation.objects.filter(payment=payment, user=request.user, refunded=False)
                for payment_relation in payment_relations:
                    user_paid = True
                    payment_relation_id = payment_relation.id
                if not user_paid and user_attending:
                    attendee = Attendee.objects.get(event=attendance_event, user=request.user)
                    if attendee:
                        user_paid = attendee.paid

                if not user_paid:
                    payment_delays = PaymentDelay.objects.filter(user=request.user, payment=payment)
                    if payment_delays:
                        payment_delay = payment_delays[0]

        context.update({
                'now': timezone.now(),
                'attendance_event': attendance_event,
                'user_anonymous': user_anonymous,
                'attendee': attendee,
                'user_attending': user_attending,
                'will_be_on_wait_list': will_be_on_wait_list,
                'rules': rules,
                'user_status': user_status,
                'place_on_wait_list': int(place_on_wait_list),
                #'position_in_wait_list': position_in_wait_list,
                'captcha_form': form,
                'user_access_to_event': user_access_to_event,
                'payment': payment,
                'user_paid': user_paid,
                'payment_delay': payment_delay,
                'payment_relation_id': payment_relation_id,
        })

    return render(request, 'events/details.html', context)

def get_attendee(attendee_id):
    return get_object_or_404(Attendee, pk=attendee_id)

@login_required
def attendEvent(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if not event.is_attendance_event():
        messages.error(request, _(u"Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    if not request.POST:
        messages.error(request, _(u'Vennligst fyll ut skjemaet.'))
        return redirect(event)

    form = CaptchaForm(request.POST, user=request.user)

    if not form.is_valid():
        for field,errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

        return redirect(event)

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    attendance_event = event.attendance_event

    response = event.attendance_event.is_eligible_for_signup(request.user);

    if response['status']:
        ae = Attendee(event=attendance_event, user=request.user)
        if 'note' in form.cleaned_data:
            ae.note = form.cleaned_data['note']
        ae.save()
        messages.success(request, _(u"Du er nå påmeldt på arrangementet!"))

        try:
            payment = Payment.objects.get(content_type=ContentType.objects.get_for_model(AttendanceEvent),
                object_id=event_id)
        except Payment.DoesNotExist:
            payment = None

        #If payment_type is delay, Create delay object
        if payment and not event.attendance_event.is_on_waitlist(request.user):
            if payment.payment_type == 3:
                deadline = timezone.now() + timedelta(days=payment.delay)
                payment.create_payment_delay(request.user, deadline)
                #TODO send mail

        return redirect(event)
    else:
        messages.error(request, response['message'])
        return redirect(event)

@login_required
def unattendEvent(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if not event.is_attendance_event():
        messages.error(request, _(u"Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    attendance_event = event.attendance_event

    # Check if user is attending
    if len(Attendee.objects.filter(event=attendance_event, user=request.user)) == 0:
        messages.error(request, _(u"Du er ikke påmeldt dette arrangementet."))
        return redirect(event)

    # Check if the deadline for unattending has passed
    if attendance_event.unattend_deadline < timezone.now() and not attendance_event.is_on_waitlist(request.user):
        messages.error(request, _(u"Avmeldingsfristen for dette arrangementet har utløpt."))
        return redirect(event)

    if attendance_event.event.event_start < timezone.now():
        messages.error(request, _(u"Dette arrangementet har allerede startet."))
        return redirect(event)

    try:
        payment = Payment.objects.get(content_type=ContentType.objects.get_for_model(AttendanceEvent),
            object_id=event_id)
    except Payment.DoesNotExist:
        payment = None

    #Delete payment delays connected to the user and event
    if payment:

        payments = PaymentRelation.objects.filter(payment=payment, user=request.user, refunded=False)

        #Return if someone is trying to unatend without refunding
        if payments:
            messages.error(request, _(u'Du har betalt for arrangementet og må refundere før du kan melde deg av'))
            return redirect(event)

        delays = PaymentDelay.objects.filter(payment=payment, user=request.user)
        for delay in delays:
            delay.delete()


    event.attendance_event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=request.user)
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

    #Filters events that are restricted
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
        messages.error(request, _(u"Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if event not in get_group_restricted_events(request.user):
        messages.error(request, _(u'Du har ikke tilgang til listen for dette arrangementet.'))
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
        messages.error(request, _(u"Dette er ikke et påmeldingsarrangement."))
        return redirect(event)

    # Check access
    if event not in get_group_restricted_events(request.user):
        messages.error(request, _(u'Du har ikke tilgang til å vise denne siden.'))
        return redirect(event)

    all_attendees = list(event.attendance_event.attendees_qs)
    attendees_on_waitlist = list(event.attendance_event.waitlist_qs)
    attendees_not_paid = list(event.attendance_event.attendees_not_paid)

    if request.method == 'POST':

        # Decide from email
        from_email = 'kontakt@online.ntnu.no'
        from_email_value = request.POST.get('from_email')

        if from_email_value == '1' or from_email_value == '4':
            from_email = settings.EMAIL_ARRKOM
        elif from_email_value == '2':
            from_email = settings.EMAIL_BEDKOM
        elif from_email_value == '3':
            from_email = settings.EMAIL_FAGKOM
        elif from_email_value == '5':
            from_email = settings.EMAIL_EKSKOM

        # Decide who to send mail to
        to_emails = []
        to_emails_value = request.POST.get('to_email')

        if to_emails_value == '1':
            to_emails = [attendee.user.email for attendee in all_attendees]
        elif to_emails_value == '2':
            to_emails = [attendee.user.email for attendee in attendees_on_waitlist]
        else:
            to_emails = [attendee.user.email for attendee in attendees_not_paid]

        context = {}
        context['message'] = request.POST.get('message')
        context['signature'] = u'Vennlig hilsen Linjeforeningen Online.\n(Denne eposten kan besvares til %s)' % from_email
        message = render_to_string('events/email/mail_participants_tpl.txt', context)
        subject = request.POST.get('subject')

        # Send mail
        try:
            if EmailMessage(unicode(subject), unicode(message), from_email, [], to_emails).send():
                messages.success(request, _(u'Mailen ble sendt'))
                return redirect(event)
            else:
                messages.error(request, _(u'Vi klarte ikke å sende mailene dine. Prøv igjen'))
                return redirect(event)
        except Exception, e:
            messages.error(request, str(e))
            return redirect(event)

    return render(request, 'events/mail_participants.html', {
        'all_attendees' : all_attendees, 'attendees_on_waitlist': attendees_on_waitlist, 'attendees_not_paid': attendees_not_paid, 'event' : event})


# API v1
import django_filters
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from apps.events.serializers import EventSerializer, AttendanceEventSerializer, CompanyEventSerializer
from apps.events.filters import EventDateFilter


class EventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)
    filter_class = EventDateFilter
    filter_fields = ('event_start', 'event_end', 'id',)
    ordering_fields = ('event_start', 'event_end', 'id',)
    ordering = ('id',)

    def get_queryset(self):
        return Event.objects.filter(
            Q(group_restriction__isnull=True) | Q(group_restriction__groups__in=self.request.user.groups.all())).\
            distinct()


class AttendanceEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AttendanceEvent.objects.all()
    serializer_class = AttendanceEventSerializer
    permission_classes = (AllowAny,)


class CompanyEventViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = CompanyEvent.objects.all()
    serializer_class = CompanyEventSerializer
    permission_classes = (AllowAny,)
