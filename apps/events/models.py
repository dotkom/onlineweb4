#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class Event(models.Model):
    """
    Base class for Event-objects
    """
    author = models.ForeignKey(User, related_name='author')
    title = models.CharField(_('title'), max_length=100)
    event_start = models.DateTimeField(_('start_date'))
    event_end = models.DateTimeField(_('end_date'))
    location = models.CharField(_('location'), max_length=100)
    description = models.TextField(_('description'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

class AttendanceEvent(Event):
    max_capacity = models.PositiveIntegerField(_('max_capacity'))
    registration_start = models.DateTimeField(_('registration_start'))
    registration_end = models.DateTimeField(_('registration_end'))

    class Meta:
        verbose_name = _('AttendanceEvent')
        verbose_name_plural = _('AttendanceEvents')
