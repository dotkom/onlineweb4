#-*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from apps.userprofile.models import UserProfile
from apps.companyprofile.models import Company
from apps.userprofile.models import FIELD_OF_STUDY_CHOICES
from filebrowser.fields import FileBrowseField

class Event(models.Model):
    """
    Base class for Event-objects.
    """

    IMAGE_FOLDER = "images/events"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

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
    image = FileBrowseField(_(u"bilde"), 
        max_length=200, directory=IMAGE_FOLDER,
        extensions=IMAGE_EXTENSIONS, null=False, blank=False)
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

    def is_attendance_event(self):
        """ Returns true if the event is an attendance event """
        return True if self.attendance_event else False

    def is_eligible_for_signup(self, user):
        """
        Checks if a user can attend a specific event
        This method checks for:
            AttendanceEvent
            Waitlist
            Room on event
            Rules
            Marks
        @param User object with userprofile
        TODO:
            Exception handling
            Message handling (Return what went wrong. Tuple? (False, message))
        """

        response = {"status" : False, "message" : ""};

        #Check first if this is an attendance event
        if not self.is_attendance_event():
            response['message'] = _(u"Dette er ikke et påmeldingsarrangement.");
            return response

        #Room for me on the event?
        if not self.attendance_event.room_on_event:
            response['message'] = _(u"Det er ikke mer plass på dette arrangementet.");
            return response

        #Are there any rules preventing me from attending?
        try:
            if not self.attendance_event.rules_satisfied(user):
                response['message'] = _(u"Du har ikke tilgang til dette arrangmentet akkurat nå.");
                return response
        except Exception, e:
            response['message'] = e;
            return response

        #Do I have any marks preventing me from attending?
        #TODO check for marks

        response['status'] = True;
        return response

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

    def satisfied(self, user, registration_start):
        """ Override method """
        #Get userprofile for user

        try:
            userprofile = UserProfile.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            return False

        # If the user has the same FOS as this rule    
        if (self.field_of_study == userprofile.field_of_study):
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return True 
        return False

    def __unicode__(self):
        return '<FOS: ' + str(FIELD_OF_STUDY_CHOICES[self.field_of_study][1]) + ' offset: ' + str(self.offset) + 'hours>'


class GradeRule(Rule):
    grade = models.SmallIntegerField(_(u'klassetrinn'), null=False)

    def satisfied(self, user):
        try:
            userprofile = UserProfile.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            return False

        # If the user has the same FOS as this rule    
        if (self.grade == userprofile.year):
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return True 
        return False

    def __unicode__(self):
        return '<Grade: ' + str(self.grade) + ' offset: ' + str(self.offset) + ' hours>'


class UserGroupRule(Rule):
    #ldapmagic
    group = models.ForeignKey(Group, blank=False, null=False)

    def satisfied(self, user, registration_start):
        """ Override method """
        if self.group in user.groups.all():
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return True 
        return False

    def __unicode__(self):
        return '<Group: ' + str(self.group) + ' offset: ' + str(self.offset) + ' hours>'


class RuleBundle(models.Model):
    """
    Access restriction rule object
    """
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, null=True, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, null=True, blank=True)
    user_group_rules = models.ManyToManyField(UserGroupRule, null=True, blank=True)

    def satisfied(self, user, registration_start):

        if self.grade_rules:
            for grade_rule in self.grade_rules.all():
                if grade_rule.satisfied(user, registration_start):    
                    return True

        if self.field_of_study_rules:
            for fos_rule in self.field_of_study_rules.all():
                if fos_rule.satisfied(user, registration_start):
                    return True

        if self.user_group_rules:
            for user_group_rule in self.user_group_rules.all():
                if user_group_rule.satisfied(user, registration_start):
                    return True

        return False

    def __unicode__(self):
        string = ""
        for obj in self.field_of_study_rules.all():
            string += unicode(obj) + ' '
        for obj in self.grade_rules.all():
            string += unicode(obj) + ' '
        for obj in self.user_group_rules.all():
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

    max_capacity = models.PositiveIntegerField(_(u'maks-kapasitet'))
    waitlist = models.BooleanField(_(u'venteliste'), default=False)
    registration_start = models.DateTimeField(_(u'registrerings-start'))
    registration_end = models.DateTimeField(_(u'registrerings-slutt'))

    #Access rules
    rule_bundles = models.ManyToManyField(RuleBundle, blank=True, null=True)

    @property
    def room_on_event(self):
        return True if (self.attendees.count() < self.max_capacity) or self.waitlist else False

    def rules_satisfied(self, user):
        """
        Checks a user against rules applied to an attendance event
        """
        # If there are no rule_bundles on this object, no one is allowed
        if not self.rule_bundles:
            return True

        for rule_bundle in self.rule_bundles.all():
            if rule_bundle.satisfied(user, self.registration_start):
                return True
            
        return False

    def is_attendee(self, user):
        return self.attendees.filter(user=user)

    def __unicode__(self):
        return self.event.title

    class Meta:
        verbose_name = _(u'paamelding')
        verbose_name_plural = _(u'paameldinger')

class CompanyEvent(models.Model):
    """
    Company relation to AttendanceEvent
    """    
    company = models.ForeignKey(Company, verbose_name=_(u'bedrifter'))
    event = models.ForeignKey(Event, verbose_name=_(u'arrangement'))

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
    attended = models.BooleanField(_(u'var tilstede'))

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['timestamp']
