#-*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.events.models import Event

def get_group_restricted_events(user):
    """ Returns a queryset of events with attendance_event that a user has access to """
    types_allowed = []

    groups = user.groups.all()

    if reduce(lambda r, g: g.name in ['Hovedstyret', 'dotKom'] or r, groups, False):
        return Event.objects.filter(attendance_event__isnull=False)

    for group in groups:
        if group.name == 'arrKom':
            types_allowed.append(1) # sosialt 
            types_allowed.append(4) # utflukt

        if group.name == 'bedKom':
            types_allowed.append(2) # bedriftspresentasjon 

        if group.name == 'fagKom':
            types_allowed.append(3) # kurs

    return Event.objects.filter(attendance_event__isnull=False, event_type__in=types_allowed)


def handle_waitlist_bump(event, host, attendees, payment=None):

    title = u'Du har fått plass på %s' % (event.title)

    extended_deadline = timezone.now() + timedelta(days=2)
    message = u'Du har stått på venteliste for arrangementet "%s" og har nå fått plass.\n' % (unicode(event.title))

    if payment:
        if payment.payment_type == 1: #Instant
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, extended_deadline)
            message += u"Dette arrangementet krever betaling og du må betale innen 48 timer."
        
        elif payment.payment_type == 2: #Deadline
            if payment.deadline > extended_deadline: #More than 2 days left of payment deadline
                message += u"Dette arrangementet krever betaling og fristen for og betale er %s" % (payment.deadline.strftime('%-d %B %Y kl: %H:%M'))
            else: #The deadline is in less than 2 days
                for attendee in attendees:
                    payment.create_payment_delay(attendee.user, extended_deadline)
                message += u"Dette arrangementet krever betaling og du har 48 timer på å betale"
        
        elif payment.payment_type == 3: #Delay
            deadline = timezone.now() + timedelta(days=payment.delay)
            for attendee in attendees:
                payment.create_payment_delay(attendee.user, deadline)
            message += u"Dette arrangementet krever betaling og du må betale innen %d dager." % (payment.delay)
        if len(payment.prices()) == 1:
            message += u"\nPrisen for dette arrangementet er %skr." % (payment.prices()[0].price)
        # elif len(payment.prices()) >= 2:
        #     message += u"\nDette arrangementet har flere prisklasser:"
        #     for payment_price in payment.prices():
        #         message += "\n%s: %skr" % (payment_price.description, payment_price.price)
    else:
        message += u"Det kreves ingen ekstra handling fra deg med mindre du vil melde deg av."

    message += u"\n\nFor mer info:"
    message += u"\nhttp://%s%s" % (host, event.get_absolute_url())

    for attendee in attendees:
        send_mail(title, message, settings.DEFAULT_FROM_EMAIL, [attendee.user.email])
