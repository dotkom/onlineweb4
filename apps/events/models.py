#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.companyprofile.models import Company
from apps.userprofile.models import FIELD_OF_STUDY_CHOICES

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
    
    @property
    def number_of_attendees_on_waiting_list(self):
        """
        Sjekker antall på venteliste
        """
        waiting = self.attendance_event.attendees.count() - self.attendance_event.max_capacity
        return waiting if waiting else 0

    @property
    def number_of_attendees_not_on_waiting_list(self):
        """
        Sjekker hvor mange attendees som har meldt seg på innen max_grensa
        """
        not_waiting = self.attendance_event.attendees.count()

        return not_waiting if not_waiting < self.attendance_event.max_capacity else self.attendance_event.max_capacity

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('arrangement')
        verbose_name_plural = _('arrangement')

"""
 BEGIN ACCESS RESTRICTION --------------------------------------------------------------------------
"""

class RuleOffset(models.Model):
    offset = models.IntegerField(_(u'antall timer'), blank=True)
    def __unicode__(self):
        return str(self.offset)



class Rule(models.Model):
    """
    Super class for a rule object
    """
    offset = models.ForeignKey(RuleOffset, primary_key=False, null=True, blank=True, default=0)

    def satisfied(self, user):
        """ Checks if a user """
        return True

    def __unicode__(self):
        return 'Rule'



class FieldOfStudyRule(Rule):
    field_of_study = models.SmallIntegerField(_(u'studieretning'), choices=FIELD_OF_STUDY_CHOICES, null=False)

    def satisfied(self, user):
        """ Override method """
        return True

    def __unicode__(self):
        return str(FIELD_OF_STUDY_CHOICES[self.field_of_study][1])

class GradeRule(Rule):
    grade = models.SmallIntegerField(_(u'klassetrinn'), null=False)

    def satisfied(self, user):
        """ Override method """
        return True

    def __unicode__(self):
        return str(self.grade)

class UserGroupRule(Rule):
    #ldapmagic

    def satisfied(self, user):
        """ Override method """
        return True

class RuleBundle(models.Model):
    """
    Access restriction rule object
    """
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, null=True, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, null=True, blank=True)

    def __unicode__(self):
        string = ""
        for obj in self.field_of_study_rules.all():
            string += unicode(obj) + ' '
        for obj in self.grade_rules.all():
            string += unicode(obj) + ' '
        return string

"""
 END ACCESS RESTRICTION --------------------------------------------------------------------------
"""


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

    #Access rules
    rule_bundles = models.ManyToManyField(RuleBundle, blank=True, null=True)

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
