#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from apps.companys.models import Company


class Event(models.Model):
    """
    Base class for Event-objects
    """
    event_id = models.AutoField(primary_key=True)

    author = models.ForeignKey(User, related_name="author")
    title = models.CharField(_("title"), max_length=100)
    start_date = models.DateTimeField(_("start_date"))
    end_date = models.DateTimeField(_("end_date"))
    location = models.CharField(_("location"), max_length=100)
    description = models.TextField(_("description"))

    TYPE_CHOICES = (
        (1, "Sosialt"),
        (2, "Bedriftspresentasjon"),
        (3, "Kurs"),
        (4, "Utflukt"),
        (5, "Annet")
    )
    type = models.SmallIntegerField("type", choices=TYPE_CHOICES)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")


class EventCompanyExt(models.Model):
    """
    A company extension of Event.

    If an event is somehow connected to a company, extend it with this.
    An event can only be affiliated with exactly one event.
    """
    event = models.OneToOneField(Event, primary_key=True)
    company = models.ForeignKey(Company)


class NewsExt(models.Model):
    """A news extension of Event.
    Adds fields that is necessary for an event to become a news story"""

    #TODO: zope.implements(interface)
    event = models.OneToOneField(Event, primary_key=True)

    post_date = models.DateTimeField(_("posted"), auto_now_add=True)
    last_edited_date = models.DateTimeField(_("last edited"), auto_now=True)
    last_edited_by = models.ForeignKey(User, verbose_name=_("last edited by"),
        editable=False, related_name="last_edits")
    expiration_date = models.DateTimeField(_("expiration date"))
    #TODO: image

    @property
    def title(self):
        #TODO: return event.title
        pass

    @property
    def author(self):
        #TODO: return event.author
        pass
