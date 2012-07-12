#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class Event(models.Model):
    """
    Base class for Event-objects
    """
    author = models.ForeignKey(User)
    title = models.CharField(_('title'), max_length=100)
    start_date = models.DateTimeField(_('start_date'))
    end_date = models.DateTimeField(_('end_date'))
    location = models.CharField(_('location'), max_length=100)
    description = models.TextField(_('description'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

