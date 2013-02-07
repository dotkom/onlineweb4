#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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
    description = models.TextField(_('beskrivelse'))
    event_type = models.SmallIntegerField(_('type'), choices=TYPE_CHOICES, null=False)

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

    def __unicode__(self):
        return self.event.title

    class Meta:
        verbose_name = _('paamelding')
        verbose_name_plural = _('paameldinger')


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
