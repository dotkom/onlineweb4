#-*- coding: utf-8 -*-

import datetime
from collections import OrderedDict

from django.utils import timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.core.signing import Signer, BadSignature
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType 

import icalendar
import watson

from apps.authentication.models import OnlineUser as User
from apps.events.forms import CaptchaForm
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.events.pdf_generator import EventPDF
from apps.events.utils import get_group_restricted_events
from apps.payment.models import Payment, PaymentRelation

def index(request):
    context = {}
    if request.user and request.user.is_authenticated():
        signer = Signer()
        context['signer_value'] = signer.sign(request.user.username)
        context['personal_ics_path'] = request.build_absolute_uri(reverse('events_personal_ics', args=(context['signer_value'],)))
    return render(request, 'events/index.html', context)

def details(request, event_id, event_slug):
    event = get_object_or_404(Event, pk=event_id)

    is_attendance_event = False
    user_anonymous = True
    user_attending = False
    place_on_wait_list = 0
    will_be_on_wait_list = False
    rules = []
    user_status = False

    user_access_to_event = False
    if request.user:
        if event in get_group_restricted_events(request.user):
            user_access_to_event = True

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

    payments = Payment.objects.filter(content_type=ContentType.objects.get_for_model(Event), object_id=event_id)
    payment_relation = None

    if payments:
        request.session['event_id'] = event.id
        request.session['payment_ids'] = [payment.id for payment in payments]

        payment_relation = PaymentRelation.objects.filter(payment__in=payments, user=request.user)
        if payment_relation:
            payment_relation = payment_relation[0]

    context = {'event': event, 'ics_path': request.build_absolute_uri(reverse('event_ics', args=(event.id,)))}
    if is_attendance_event:
        context.update({
                'now': timezone.now(),
                'attendance_event': attendance_event,
                'user_anonymous': user_anonymous,
                'user_attending': user_attending,
                'will_be_on_wait_list': will_be_on_wait_list,
                'rules': rules,
                'user_status': user_status,
                'place_on_wait_list': int(place_on_wait_list),
                #'position_in_wait_list': position_in_wait_list,
                'captcha_form': form,
                'user_access_to_event': user_access_to_event,
                'payments': payments,
                'payment_relation': payment_relation,
        })
    return render(request, 'events/details.html', context)

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
        for field,errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

        return redirect(event)

    # Check if the user is eligible to attend this event.
    # If not, an error message will be present in the returned dict
    attendance_event = event.attendance_event

    response = event.is_eligible_for_signup(request.user);

    if response['status']:   
        ae = Attendee(event=attendance_event, user=request.user)
        if 'note' in form.cleaned_data:
            ae.note = form.cleaned_data['note']
        ae.save()
        messages.success(request, _(u"Du er nå påmeldt på arrangementet!"))
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
        kwargs['attendance_event__attendees__user'] = request.user

    events = Event.objects.filter(**kwargs).order_by('event_start').prefetch_related(
            'attendance_event', 'attendance_event__attendees', 'attendance_event__reserved_seats',
            'attendance_event__reserved_seats__reservees')
    
    if query:
        for result in watson.search(query, models=(events,)):
            results.append(result.object)
        return results[:10]

    return events


@login_required()
@user_passes_test(lambda u: u.groups.filter(name='Komiteer').count() == 1)
def generate_pdf(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    groups = request.user.groups.all()
    if not (groups.filter(name='dotKom').count() == 1 or groups.filter(name='Hovedstyret').count() == 1):
        if event.event_type == 1 and not groups.filter(name='arrKom').count() == 1:
            messages.error(request, _(u'Du har ikke tilgang til listen for dette arrangementet.'))
            return redirect(event)

        if event.event_type == 2 and not groups.filter(name='bedKom').count() == 1:
            messages.error(request, _(u'Du har ikke tilgang til listen for dette arrangementet.'))
            return redirect(event)

        if event.event_type == 3 and not groups.filter(name='fagKom').count() == 1:
            messages.error(request, _(u'Du har ikke tilgang til listen for dette arrangementet.'))  
            return redirect(event)

    return EventPDF(event).render_pdf()

def calendar_export(request, event_id=None, user=None):
    cal = icalendar.Calendar()
    cal.add('prodid', '-//Online//Onlineweb//EN')
    cal.add('version', '2.0')
    filename = 'online'
    if event_id:
        # Single event
        try:
            events = [Event.objects.get(id=event_id)]
        except Event.DoesNotExist:
            events = []
        filename = str(event_id)
    elif user:
        # Personalized calendar
        # This calendar is publicly available, but the url is not guessable so data should not be leaked to everyone
        signer = Signer()
        try:
            username = signer.unsign(user)
            user = User.objects.get(username=username)
        except (BadSignature, User.DoesNotExist):
            user = None
        if user:
            # Getting all events that the user has/is participating in
            events = Event.objects.filter(attendance_event__attendees__user=user).order_by('event_start').prefetch_related(
            'attendance_event', 'attendance_event__attendees')
            filename = username
        else:
            events = []
    else:
        # All events that haven't ended yet
        events = Event.objects.filter(event_end__gt=timezone.now()).order_by('event_start')
        filename = 'events'

    for event in events:
        cal_event = icalendar.Event()

        cal_event.add('dtstart', event.event_start)
        cal_event.add('dtend', event.event_end)
        cal_event.add('location', event.location)
        cal_event.add('summary', event.title)
        cal_event.add('description', event.ingress_short)
        cal_event.add('uid', 'event-' + str(event.id) + '@online.ntnu.no')

        cal.add_component(cal_event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Type'] = 'text/calendar; charset=utf-8';
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.ics'

    return response


@login_required
def mail_participants(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if not event.attendance_event:
        return HttpResponse(status=503)

    # Check access
    if not event in get_group_restricted_events(request.user):
        messages.error(request, _(u'Du har ikke tilgang til å vise denne siden.'))
        return redirect(event)

    all_attendees = event.attendance_event.attendees
    attendees_on_waitlist = event.attendance_event.waitlist_qs
    attendees_not_paid = event.attendees_not_paid

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

        signature = u'\n\nVennlig hilsen Linjeforeningen Online.\n(Denne eposten kan besvares til %s)' % from_email

        # Decide who to send mail to 
        to_emails = []
        to_emails_value = request.POST.get('to_email')

        if to_emails_value == '1':
            to_emails = [attendee.user.email for attendee in all_attendees.all()]
            print to_emails
        elif to_emails_value == '2':
            to_emails = [attendee.user.email for attendee in attendees_on_waitlist.all()]
        else:
            to_emails = [attendee.user.email for attendee in attendees_not_paid.all()]

        message = '%s%s' % (request.POST.get('message'), signature)
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
