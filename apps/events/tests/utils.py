from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm, get_perms_for_model

from apps.authentication.constants import GroupType
from apps.authentication.models import GroupMember, OnlineGroup, OnlineUser
from apps.companyprofile.models import Company
from apps.events.models.Attendance import CompanyEvent
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation

from ..constants import EventType
from ..models import AttendanceEvent, Attendee, Event


def generate_event(
    event_type=EventType.BEDPRES, organizer: Group = None, attendance=True
) -> Event:
    if organizer is None:
        organizer = create_committee_group()
    event = G(Event, event_type=event_type, organizer=organizer)
    if attendance:
        G(AttendanceEvent, event=event)
    return event


def generate_company_event(
    event_type=EventType.BEDPRES, organizer: Group = None, attendance=True
) -> Event:
    onlinecorp: Company = G(Company, name="onlinecorp")
    bedpres_with_onlinecorp = generate_event(
        event_type=event_type, organizer=organizer, attendance=attendance
    )
    G(CompanyEvent, company=onlinecorp, event=bedpres_with_onlinecorp)
    return bedpres_with_onlinecorp


def generate_attendance_event(*args, **kwargs) -> AttendanceEvent:
    event = G(Event)
    return G(AttendanceEvent, *args, event=event, **kwargs)


def generate_payment(event: Event, *args, **kwargs) -> Payment:
    payment = G(
        Payment,
        *args,
        object_id=event.id,
        content_type=ContentType.objects.get_for_model(AttendanceEvent),
        **kwargs,
    )
    G(PaymentPrice, payment=payment)
    return payment


def attend_user_to_event(event: Event, user: OnlineUser) -> Attendee:
    return G(Attendee, event=event.attendance_event, user=user)


def pay_for_event(event: Event, user: OnlineUser, *args, **kwargs) -> PaymentRelation:
    return G(
        PaymentRelation,
        *args,
        payment=event.attendance_event.payment(),
        user=user,
        **kwargs,
    )


def add_payment_delay(payment: Payment, user: OnlineUser) -> PaymentDelay:
    return G(PaymentDelay, payment=payment, user=user)


def generate_user(username: str, *args, **kwargs) -> OnlineUser:
    user = G(
        OnlineUser,
        *args,
        username=username,
        ntnu_username=username,
        phone_number="12345678",
        is_active=True,
        **kwargs,
    )
    return user


def generate_attendee(event: Event, username: str) -> Attendee:
    return attend_user_to_event(event, generate_user(username))


def add_to_committee(user: OnlineUser, group: Group = None) -> OnlineUser:
    committee_group = create_committee_group()
    add_to_group(committee_group, user)

    if group:
        add_to_group(group, user)

    return user


def create_committee_group(group: Group = None):
    if not group:
        group: Group = G(Group)
    G(OnlineGroup, group=group, group_type=GroupType.COMMITTEE)

    return group


def add_to_group(group: Group, user: OnlineUser) -> GroupMember:
    try:
        online_group = OnlineGroup.objects.get(group=group)
    except OnlineGroup.DoesNotExist:
        online_group: OnlineGroup = G(OnlineGroup)
    member: GroupMember = G(GroupMember, group=online_group, user=user)
    return member


def add_event_permissions(group: Group):
    perms = get_perms_for_model(Event)
    for perm in perms:
        assign_perm(perm, group)
