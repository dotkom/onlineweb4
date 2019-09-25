# -*- coding: utf-8 -*-
from django.urls import reverse

from apps.authentication.models import OnlineUser as User
from apps.events.models import Attendee
from apps.payment.models import Payment


def _get_attendee(attendee_id):
    try:
        return Attendee.objects.get(pk=attendee_id)
    except Attendee.DoesNotExist:
        return None


def event_ajax_handler(event, request):
    action = request.POST['action']
    administrating_user = request.user

    if action == 'attended':
        attendee = _get_attendee(request.POST['attendee_id'])
        if not attendee:
            return {'message': 'Fant ingen påmeldte med oppgitt ID (%s).' % request.POST['attendee_id'],
                    'status': 400}
        return handle_attended(attendee)
    elif action == 'paid':
        attendee = _get_attendee(request.POST['attendee_id'])
        if not attendee:
            return {'message': 'Fant ingen påmeldte med oppgitt ID (%s).' % request.POST['attendee_id'],
                    'status': 400}
        return handle_paid(attendee)
    elif action == 'add_attendee':
        return handle_add_attendee(event, request.POST['user_id'])
    elif action == 'remove_attendee':
        return handle_remove_attendee(event, request.POST['attendee_id'], administrating_user)
    else:
        raise NotImplementedError


def handle_attended(attendee):
    """
    Toggle attending-status of an attendee between attending and not attending
    :param attendee_id: ID of attendee wanted to toggle
    :return:
    """
    attendee.attended = not attendee.attended
    attendee.save()

    return {'message': 'OK', 'status': 200}


def handle_paid(attendee):
    """
    Toggle paid status of an attendee between paid and not paid
    :param attendee_id: ID of attendee wanted to toggle
    :return:
    """
    attendee.paid = not attendee.paid
    attendee.save()

    return {'message': 'OK', 'status': 200}


def handle_add_attendee(event, user_id):
    resp = {}
    if event.attendance_event.number_of_seats_taken >= event.attendance_event.max_capacity:
        if not event.attendance_event.waitlist:
            return 'Det er ingen ledige plasser på %s.' % event.title

    user = User.objects.filter(pk=user_id)
    if user.count() != 1:
        return 'Fant ingen bruker med oppgitt ID (%s).' % user_id
    user = user[0]
    if Attendee.objects.filter(user=user, event=event.attendance_event).count() != 0:
        return '%s er allerede påmeldt %s.' % (user.get_full_name(), event.title)

    attendee = Attendee(user=user, event=event.attendance_event)
    attendee.save()

    resp['message'] = '%s ble meldt på %s' % (user.get_full_name(), event)
    if Payment.objects.filter(object_id=event.attendance_event.pk).count() != 0:
        resp['is_payment_event'] = True
    else:
        resp['is_payment_event'] = False

    resp['attendees'] = []

    for number, a in enumerate(attendee.event.attending_attendees_qs):
        resp['attendees'].append({
            'number': number+1,
            'id': a.id,
            'first_name': a.user.first_name,
            'last_name': a.user.last_name,
            'year_of_study': a.user.year,
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
    return resp


def handle_remove_attendee(event, attendee_id, admin_user):
    resp = {}
    attendee = Attendee.objects.filter(pk=attendee_id)
    if attendee.count() != 1:
        return 'Fant ingen påmeldte med oppgitt ID (%s).' % attendee_id
    attendee = attendee[0]
    attendee.unattend(admin_user)
    resp['message'] = '%s ble fjernet fra %s' % (attendee.user.get_full_name(), attendee.event)
    resp['attendees'] = []
    for number, a in enumerate(attendee.event.attending_attendees_qs):
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
    return resp
