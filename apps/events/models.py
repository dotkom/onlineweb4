#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    """
    Base class for Event-objects.
    """
    author = models.ForeignKey(User, related_name='oppretter')
    title = models.CharField(_('tittel'), max_length=100)
    event_start = models.DateTimeField(_('start-dato'))
    event_end = models.DateTimeField(_('slutt-dato'))
    location = models.CharField(_('lokasjon'), max_length=100)
    description = models.TextField(_('beskrivelse'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('arrangement')
        verbose_name_plural = _('arrangement')

class AttendanceEvent(Event):
    """
    Events that require special considerations regarding attendance.
    """
    max_capacity = models.PositiveIntegerField(_('maks-kapasitet'))
    registration_start = models.DateTimeField(_('registrerings-start'))
    registration_end = models.DateTimeField(_('registrerings-slutt'))
    
    class Meta:
        verbose_name = _('påmeldingsarrangement')
        verbose_name_plural = _('påmeldingsarrangement')


class Attendee(models.Model):
    """
    User relation to AttendanceEvent.
    """
    user = models.ForeignKey(User)
    event = models.ForeignKey(AttendanceEvent)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    paid = models.BooleanField(_('betalt'))
    attended = models.BooleanField(_('var tilstede'))

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        unique_together = ("event", "user")
        ordering = ['timestamp']
