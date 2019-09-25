# -*- coding: utf-8 -*-
from django.urls import reverse

from apps.authentication.models import OnlineUser as User
from apps.events.models import Attendee, Event
from apps.payment.models import Payment


def _get_attendee(attendee_id):
    try:
        return Attendee.objects.get(pk=attendee_id)
    except Attendee.DoesNotExist:
        return None


def event_ajax_handler(event: Event, request):
    action = request.POST.get('action')
    administrating_user = request.user
    attendee_id = request.POST.get('attendee_id')
    user_id = request.POST.get('user_id')

    if action == 'attended':
        attendee = _get_attendee(attendee_id)
        if not attendee:
            return {'message': f'Fant ingen påmeldte med oppgitt ID ({attendee_id}).', 'status': 400}
        return handle_attended(attendee)
    elif action == 'paid':
        attendee = _get_attendee(attendee_id)
        if not attendee:
            return {'message': f'Fant ingen påmeldte med oppgitt ID ({attendee_id}).', 'status': 400}
        return handle_paid(attendee)
    elif action == 'add_attendee':
        return handle_add_attendee(event, user_id)
    elif action == 'remove_attendee':
        return handle_remove_attendee(event, attendee_id, administrating_user)
    else:
        raise NotImplementedError


def handle_attended(attendee: Attendee):
    """
    Toggle attending-status of an attendee between attending and not attending
    """
    attendee.attended = not attendee.attended
    attendee.save()

    return {'message': 'OK', 'status': 200}


def handle_paid(attendee: Attendee):
    """
    Toggle paid status of an attendee between paid and not paid
    """
    attendee.paid = not attendee.paid
    attendee.save()

    return {'message': 'OK', 'status': 200}


def _get_attendee_data(attendee_qs):
    attendees = []

    for number, a in enumerate(attendee_qs):
        attendees.append({
            'number': number + 1,
            'id': a.id,
            'first_name': a.user.first_name,
            'last_name': a.user.last_name,
            'year_of_study': a.user.year,
            'paid': a.paid,
            'extras': str(a.extras),
            'attended': a.attended,
            'link': reverse('dashboard_attendee_details', kwargs={'attendee_id': a.id})
        })

    return attendees


def _get_event_context(event: Event, response={}):
    response['attendees'] = _get_attendee_data(event.attendance_event.attending_attendees_qs)
    response['waitlist'] = _get_attendee_data(event.attendance_event.waitlist_qs)
    response['is_payment_event'] = Payment.objects.filter(object_id=event.attendance_event.pk).exists()

    return response


def handle_add_attendee(event: Event, user_id: int):
    resp = _get_event_context(event)
    if event.attendance_event.number_of_seats_taken >= event.attendance_event.max_capacity:
        if not event.attendance_event.waitlist:
            return {'message': f'Det er ingen ledige plasser på {event.title}.', 'status': 400, **resp}

    user = User.objects.filter(pk=user_id)
    if user.count() != 1:
        return {'message': f'Fant ingen bruker med oppgitt ID ({user_id}).', 'status': 400, **resp}
    user = user[0]
    if Attendee.objects.filter(user=user, event=event.attendance_event).count() != 0:
        return {'message': f'{user} er allerede påmeldt {event.title}.', 'status': 400, **resp}

    attendee = Attendee(user=user, event=event.attendance_event)
    attendee.save()

    resp = _get_event_context(event, resp)
    return {'message': f'{user} ble meldt på {event}', 'status': 200, **resp}


def handle_remove_attendee(event: Event, attendee_id: int, admin_user: User):
    resp = _get_event_context(event)
    attendee = Attendee.objects.filter(pk=attendee_id)
    if attendee.count() != 1:
        return {'message': f'Fant ingen påmeldte med oppgitt ID ({attendee_id}).', 'status': 400, **resp}
    attendee = attendee[0]
    attendee.unattend(admin_user)

    resp = _get_event_context(event, resp)
    return {'message': f'{attendee.user} ble fjernet fra {attendee.event}', 'status': 200, **resp}
