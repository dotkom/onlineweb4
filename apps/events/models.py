#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from apps.companys.models import Company


class Event(models.Model):
    """
    Base class for Event-objects.
    """
    event_id = models.AutoField(primary_key=True)

    author = models.ForeignKey(User, related_name="author")
    title = models.CharField(_("title"), max_length=100)
    start_date = models.DateTimeField(_("start_date"))
    end_date = models.DateTimeField(_("end_date"))
    location = models.CharField(_("location"), max_length=100)
    description = models.TextField(_("description"))

    TYPE_CHOICES = (
        (1, _("social")),
        (2, _("enterprise presentation")),
        (3, _("course")),
        (4, _("excursion")),
        (5, _("other")),
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
    event = models.OneToOneField(
            Event,
            primary_key=True,
            related_name="company")
    company = models.ForeignKey(Company)


class NewsExt(models.Model):
    """A news extension of Event.
    Adds fields that is necessary for an event to become a news story"""

    #XXX: zope.implements(interface) ??
    event = models.OneToOneField(
            Event,
            primary_key=True,
            related_name="news")

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


class EventAttendanceExt(models.Model):
    """
    Attendance extension of Event.
    """
    event = models.OneToOneField(
            Event,
            primary_key=True,
            related_name="attendance")

    withdraw_date = models.DateTimeField(_("withdraw_date"))
    registration_end_date = models.DateTimeField(_("registration end date"))
    registration_start_date = models.DateTimeField(
            _("registration start date"))

    gives_mark = models.BooleanField(_("gives mark"))
    waitlist_is_open = models.BooleanField(_("wait list is open"),
            default=False)

    # restriction of event
    RESTRICTION_CHOICES = (
        (1, _("All")),
        (2, _("2-5 year")),
        (3, _("3-5 year")),
        (4, _("Master"))
    )
    restriction = models.SmallIntegerField(_("restriction"),
            choices=RESTRICTION_CHOICES)
    seats = models.PositiveIntegerField(_("seats"))
    guests = models.BooleanField(_("guests"))

    attendants = models.ManyToManyField(User, through="AttendanceEntry")


class EventAttendancePaymentExt(models.Model):
    """
    EventAttendance extension for payment.
    Adds costs_money and price to the EventAttendanceExt
    """
    event = models.OneToOneField(
            EventAttendanceExt,
            primary_key=True,
            related_name="payment")
    costs_money = models.BooleanField(_("costs money"), default=False)
    price = models.IntegerField(_("price"))


class AttendanceEntry(models.Model):
    """
    A many to many table for User on EventAttendanceExt
    """
    event = models.ForeignKey(EventAttendanceExt)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    attended = models.BooleanField(_("attended"))


class PayedAttendanceEntry(models.Model):
    """
    Adds information about event payment.
    This class should not be added to AttendanceEntry if the event is
    not extended with EventAttendancePaymentExt. This is not forced in
    the database layer, due to the necessity of a big SQL query.
    """
    attendance_entry = models.OneToOneField(
            AttendanceEntry,
            related_name="payment")

    paid = models.BooleanField(_("paid"))
