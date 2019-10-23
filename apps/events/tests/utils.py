from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm, get_perms_for_model

from apps.authentication.models import Email, OnlineUser
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation

from ..models import TYPE_CHOICES, AttendanceEvent, Attendee, Event
from ..utils import get_organizer_by_event_type


def generate_event(event_type=TYPE_CHOICES[1][0], organizer=None, attendance=True) -> Event:
    if organizer is None:
        organizer = get_organizer_by_event_type(event_type)
    event = G(Event, event_type=event_type, organizer=organizer)
    if attendance:
        G(AttendanceEvent, event=event)
    return event


def generate_attendance_event(*args, **kwargs):
    event = G(Event)
    return G(AttendanceEvent, event=event, *args, **kwargs)


def generate_payment(event, *args, **kwargs) -> Payment:
    payment = G(
        Payment,
        object_id=event.id,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
        *args,
        **kwargs
    )
    G(PaymentPrice, payment=payment)
    return payment


def attend_user_to_event(event: Event, user: OnlineUser) -> Attendee:
    return G(
        Attendee,
        event=event.attendance_event,
        user=user
    )


def pay_for_event(event: Event, user: OnlineUser, *args, **kwargs) -> PaymentRelation:
    return G(
        PaymentRelation,
        payment=event.attendance_event.payment(),
        user=user,
        *args,
        **kwargs
    )


def add_payment_delay(payment: Payment, user: OnlineUser) -> PaymentDelay:
    return G(
        PaymentDelay,
        payment=payment,
        user=user
    )


def generate_user(username) -> OnlineUser:
    user = G(OnlineUser, username=username, ntnu_username=username)
    G(Email, user=user)
    return user


def generate_attendee(event, username) -> Attendee:
    return attend_user_to_event(event, generate_user(username))


def add_to_committee(user, group=None) -> OnlineUser:
    komiteer = Group.objects.get(name__iexact="Komiteer")

    if komiteer not in user.groups.all():
        user.groups.add(komiteer)

    if group:
        user.groups.add(group)

    user.is_staff = True
    user.save()
    return user


def add_event_permissions(group):
    perms = get_perms_for_model(Event)
    for perm in perms:
        assign_perm(perm, group)


def add_to_arrkom(user):
    arrkom = Group.objects.get(name__iexact='arrkom')
    add_event_permissions(arrkom)
    return add_to_committee(user, group=arrkom)


def add_to_bedkom(user):
    bedkom = Group.objects.get(name__iexact='bedkom')
    add_event_permissions(bedkom)
    return add_to_committee(user, group=bedkom)


def add_to_fagkom(user):
    fagkom = Group.objects.get(name__iexact='fagkom')
    add_event_permissions(fagkom)
    return add_to_committee(user, group=fagkom)


def add_to_trikom(user):
    trikom = Group.objects.get(name__iexact='trikom')
    add_event_permissions(trikom)
    return add_to_committee(user, group=trikom)
