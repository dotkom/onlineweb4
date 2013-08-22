#-*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from apps.authentication.models import OnlineUser as User, FIELD_OF_STUDY_CHOICES
from apps.companyprofile.models import Company
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
        @param User object
        TODO:
            Exception handling
            Message handling (Return what went wrong. Tuple? (False, message))
        """

        response = {"status" : False, "message" : ""};

        #Check first if this is an attendance event
        if not self.is_attendance_event():
            response['message'] = _(u"Dette er ikke et påmeldingsarrangement.");
            return response

        #Registration not open
        if not datetime.now() > self.attendance_event.registration_start:
            response['message'] = _(u'Påmeldingen har ikke åpnet enda.')
            return response

        #Registration closed
        if not datetime.now() < self.attendance_event.registration_end:
            response['message'] = _(u'Påmeldingen er ikke lenger åpen.')

        #Room for me on the event?
        if not self.attendance_event.room_on_event:
            response['message'] = _(u"Det er ikke mer plass på dette arrangementet.");
            return response

        #Are there any rules preventing me from attending?
        try:
            status_object = self.attendance_event.rules_satisfied(user)

            if not status_object['status']:
                if 'offset' in status_object:
                    response_message = 'Du har ikke tilgang til dette arrangementet før om ' + str(status_object['offset'] / 60 / 60) + ' timer.'
                    response['message'] = response_message
                    return response
                response['message'] = _(u"Du har ikke tilgang til dette arrangmentet.");
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
        return self.attendance_event.attendees.all()[self.attendance_event.max_capacity:]
        return [] if self.number_of_attendees_on_waiting_list is 0 else self.attendance_event.attendees[self.attendance_event.max_capacity:]

    
    def what_place_is_user_on_wait_list(self, user):
        if self.attendance_event:
            if self.attendance_event.waitlist:
                waitlist = self.wait_list
                print waitlist
                if waitlist:
                    for attendee_object in waitlist:
                        if attendee_object.user == user:
                            return list(waitlist).index(attendee_object) + 1
        return 0

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

        # If the user has the same FOS as this rule    
        if (self.field_of_study == user.field_of_study):
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return {"status": True, "message": None}
            else:
                object_with_offset = offset_datetime - now
                seconds_until_eligible = object_with_offset.seconds
                return {"status": False, "message": _(u"Du kan ikke melde deg på akkurat nå."), "offset": seconds_until_eligible}
        return {"status": False, "message": _(u"Din studieretning er en annen enn de som har tilgang til dette arrangementet.")}

    def __unicode__(self):
        offset = 'timer'
        if self.offset.offset == 1:
            offset = 'time'
        return str(FIELD_OF_STUDY_CHOICES[self.field_of_study][1]) + (' etter ' + str(self.offset.offset) + ' ' + offset if self.offset.offset > 0 else '')


class GradeRule(Rule):
    grade = models.SmallIntegerField(_(u'klassetrinn'), null=False)

    def satisfied(self, user, registration_start):
        """ Override method """

        # If the user has the same FOS as this rule    
        if (self.grade == user.year):
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return {"status": True, "message": None}
            else:
                object_with_offset = offset_datetime - now
                seconds_until_eligible = object_with_offset.seconds
                return {"status": False, "message": _(u"Du kan ikke melde deg på akkurat nå."), "offset": seconds_until_eligible}
        return {"status": False, "message": _(u"Du er ikke i et klassetrinn som har tilgang til dette arrangementet.")}

    def __unicode__(self):
        offset = 'timer'
        if self.offset.offset == 1:
            offset = 'time'
        return str(self.grade) + '. klasse' + (' etter ' + str(self.offset.offset) + ' ' + offset if self.offset.offset > 0 else '')


class UserGroupRule(Rule):
    #ldapmagic
    group = models.ForeignKey(Group, blank=False, null=False)

    def satisfied(self, user, registration_start):
        """ Override method """
        if self.group in user.groups.all():
            now = datetime.now()
            offset_datetime = registration_start + timedelta(hours=self.offset.offset)
            if offset_datetime <= now:
                return {"status": True, "message": None}
            else:
                object_with_offset = offset_datetime - now
                seconds_until_eligible = object_with_offset.seconds
                return {"status": False, "message": _(u"Du kan ikke melde deg på akkurat nå"), "offset": seconds_until_eligible}
        return {"status": False, "message": _(u"Du er ikke i en brukergruppe som har tilgang til dette arrangmentet.")}

    def __unicode__(self):
        offset = 'timer'
        if self.offset.offset == 1:
            offset = 'time'
        return str(self.group) + (' etter ' + str(self.offset.offset) + ' ' + offset if self.offset.offset > 0 else '')


class RuleBundle(models.Model):
    """
    Access restriction rule object
    """
    description = models.CharField(_(u'beskrivelse'), max_length=100)
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, null=True, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, null=True, blank=True)
    user_group_rules = models.ManyToManyField(UserGroupRule, null=True, blank=True)

    @property
    def get_rule_strings(self):
        rules = []
        for rule in self.field_of_study_rules.all():
            rules.append(unicode(rule))
        for rule in self.grade_rules.all():
            rules.append(unicode(rule))
        for rule in self.user_group_rules.all():
            rules.append(unicode(rule))
        return rules
        
        
    def satisfied(self, user, registration_start):

        errors = []
        # Used to find the largest offset the user can relate to before being eligible
        largest_offset_in_seconds = 0

        if self.grade_rules:
            for grade_rule in self.grade_rules.all():
                response =  grade_rule.satisfied(user, registration_start)
                if response['status']:
                    return {"status": True}
                else:
                    errors.append(response)

        if self.field_of_study_rules:
            for fos_rule in self.field_of_study_rules.all():
                response = fos_rule.satisfied(user, registration_start)
                if response['status']:
                    return {'status': True}
                else:
                    errors.append(response)

        if self.user_group_rules:
            for user_group_rule in self.user_group_rules.all():
                response = user_group_rule.satisfied(user, registration_start)
                if response['status']:
                    return {'status':True}
                else:
                    errors.append(response)

        # If we found errors, check if there was any that just had an offset. Then find the largest one so we can show the user when he will be eligible to register
        if errors:
            for error in errors:
                if 'offset' in error:
                    if error['offset'] > largest_offset_in_seconds:
                        largest_offset_in_seconds = error['offset']
            if largest_offset_in_seconds > 0:
                return {"status":False, "offset": largest_offset_in_seconds}
            else:
                return {"status": False, "message": "Du har ikke tilgang til dette arrangementet."}

        return {"status": False}

    def __unicode__(self):
        string = ""
        for obj in self.field_of_study_rules.all():
            string += unicode(obj) + ', '
        for obj in self.grade_rules.all():
            string += unicode(obj) + ', '
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

    @property
    def will_i_be_on_wait_list(self):
        return True if (self.attendees.count() >= self.max_capacity) and self.waitlist else False

    def rules_satisfied(self, user):
        """
        Checks a user against rules applied to an attendance event
        """
        # If there are no rule_bundles on this object, no one is allowed
        if not self.rule_bundles:
            return False

        largest_offset_in_seconds = 0
        errors = []    

        # Check all rule bundles
        # If one satisfies, return true, else check offset or append to response
        for rule_bundle in self.rule_bundles.all():
            response =  rule_bundle.satisfied(user, self.registration_start)
            if response['status']:
                return {"status": True}
            elif 'offset' in response:
                if response['offset'] > largest_offset_in_seconds:
                    largest_offset_in_seconds = response['offset']
            else:
                errors.append(response)

        if largest_offset_in_seconds > 0:
            return {"status": False, "offset": largest_offset_in_seconds}
        if errors:
            return {"status": False, "message": _(u"Du har ikke tilgang til arrangementet.")}   

        return {"status": False}

    @property
    def waitlist_enabled(self):
        return self.waitlist

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
    event = models.ForeignKey(Event, verbose_name=_(u'arrangement'), related_name='companies')

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
