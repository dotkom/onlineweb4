#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.companyprofile.models import Company

class Event(models.Model):
    """
    Base class for Event-objects.
    """

    TYPE_CHOICES = (
        (1, 'Sosialt'),
        (2, 'Bedriftspresentasjon'),
        (3, 'Kurs'),
        (4, 'Utflukt'),
        (5, 'Internt'),
        (6, 'Annet')
    )

    author = models.ForeignKey(User, related_name='oppretter')
    title = models.CharField(_('tittel'), max_length=100)
    event_start = models.DateTimeField(_('start-dato'))
    event_end = models.DateTimeField(_('slutt-dato'))
    location = models.CharField(_('lokasjon'), max_length=100)
    ingress = models.TextField(_('ingress'))
    description = models.TextField(_('beskrivelse'))
    event_type = models.SmallIntegerField(_('type'), choices=TYPE_CHOICES, null=False)

    def feedback_users(self):
        users = []
        if self.attendance_event.attendees.all():
            for attendee in self.attendance_event.attendees.all():
                users.append(attendee.user)
        return users

    @property
    def number_of_attendees_on_waiting_list(self):
        """
        Sjekker antall på venteliste
        """
        waiting = self.attendance_event.attendees.count() - self.attendance_event.max_capacity
        return 0 if waiting < 0 else waiting

    @property
    def number_of_attendees_not_on_waiting_list(self):
        """
        Sjekker hvor mange attendees som har meldt seg på innen max_grensa
        """
        not_waiting = self.attendance_event.attendees.count()

        return not_waiting if not_waiting < self.attendance_event.max_capacity else self.attendance_event.max_capacity

    @property
    def wait_list(self):
        return [] if self.number_of_attendees_on_waiting_list is 0 else self.attendance_event.attendees[self.attendance_event.max_capacity:]

    @models.permalink
    def get_absolute_url(self):
        return reverse('apps.event.views.details', args=[str(self.id)])

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('arrangement')
        verbose_name_plural = _('arrangement')


class AttendanceEvent(models.Model):
    """
    Events that require special considerations regarding attendance.
    """
    event = models.OneToOneField(
        Event,
        primary_key=True,
        related_name='attendance_event')

    max_capacity = models.PositiveIntegerField(_('maks-kapasitet'))
    registration_start = models.DateTimeField(_('registrerings-start'))
    registration_end = models.DateTimeField(_('registrerings-slutt'))

    def is_attendee(self, user):
        return self.attendees.filter(user=user)

    def __unicode__(self):
        return self.event.title

    class Meta:
        verbose_name = _('paamelding')
        verbose_name_plural = _('paameldinger')


class CompanyEvent(models.Model):
    """
    Company relation to AttendanceEvent
    """    
    company = models.ForeignKey(Company, verbose_name=_('bedrifter'))
    event = models.ForeignKey(Event, verbose_name=_('arrangement'))

    class Meta:
        verbose_name =_('bedrift')
        verbose_name_plural = _('bedrifter')


class Attendee(models.Model):
    """
    User relation to AttendanceEvent.
    """
    event = models.ForeignKey(AttendanceEvent, related_name="attendees")
    user = models.ForeignKey(User)

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    attended = models.BooleanField(_('var tilstede'))

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['timestamp']
