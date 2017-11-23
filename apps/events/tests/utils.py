from django.contrib.auth.models import Group
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm, get_perms_for_model

from ..models import TYPE_CHOICES, AttendanceEvent, Event
from ..utils import get_organizer_by_event_type


def generate_event(event_type=TYPE_CHOICES[1][0]):
    event = G(Event, event_type=event_type, organizer=get_organizer_by_event_type(event_type))
    G(AttendanceEvent, event=event)
    return event


def add_to_committee(user, group=None):
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
