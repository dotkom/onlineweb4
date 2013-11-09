#-*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext as _

from filebrowser.fields import FileBrowseField
import watson

from apps.authentication.models import OnlineUser as User, FIELD_OF_STUDY_CHOICES
from apps.companyprofile.models import Company
from filebrowser.fields import FileBrowseField
from apps.marks.models import Mark

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
    title = models.CharField(_(u'tittel'), max_length=45)
    event_start = models.DateTimeField(_(u'start-dato'))
    event_end = models.DateTimeField(_(u'slutt-dato'))
    location = models.CharField(_(u'lokasjon'), max_length=100)
    ingress_short = models.CharField(_(u"kort ingress"), max_length=150)
    ingress = models.TextField(_(u'ingress'))
    description = models.TextField(_(u'beskrivelse'))
    image = FileBrowseField(_(u"bilde"), 
        max_length=200, directory=IMAGE_FOLDER,
        extensions=IMAGE_EXTENSIONS, null=False, blank=False)
    event_type = models.SmallIntegerField(_(u'type'), choices=TYPE_CHOICES, null=False)

    def feedback_users(self):
        users = []
        try:
            if self.attendance_event.attendees.all():
                for attendee in self.attendance_event.attendees.all():
                    users.append(attendee.user)
            return users
        except AttendanceEvent.DoesNotExist:
            return users

    def feedback_date(self):
        return self.event_start

    def feedback_title(self):
        return self.title

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
        The returned dict contains a key called 'status_code'. These codes follow the HTTP
        standard in terms of overlying scheme.
        2XX = successful
        4XX = client error (user related)
        5XX = server error (event related)
        These codes are meant as a debugging tool only. The eligibility checking is quite
        extensive, and tracking where it's going wrong is much needed.
        TODO:
            Exception handling
            Message handling (Return what went wrong. Tuple? (False, message))
        """

        response = {'status' : False, 'message' : '', 'status_code': None}

        # Check first if this is an attendance event
        if not self.is_attendance_event():
            response['message'] = _(u"Dette er ikke et påmeldingsarrangement.")
            response['status_code'] = 500
            return response

        # Registration closed
        if timezone.now() > self.attendance_event.registration_end:
            response['message'] = _(u'Påmeldingen er ikke lenger åpen.')
            response['status_code'] = 502 
            return response
        
        #
        # Offset calculations.
        #

        # Are there any rules preventing me from attending?
        # This should be checked last of the offsets, because it can completely deny you access.
        response = self.attendance_event.rules_satisfied(user)
        print 'rules response: ',
        print response
        if not response['status']:
            if 'offset' not in response:
                return response
        
        # Do I have any marks that postpone my registration date?
        active_marks = Mark.active.filter(given_to = user).count()
        if active_marks > 0:
            # Offset is currently 1 day per mark. 
            mark_offset = timedelta(days=active_marks)
            postponed_registration_start = self.attendance_event.registration_start + mark_offset
            if postponed_registration_start > timezone.now():
                if 'offset' in response and response['offset'] < postponed_registration_start or 'offset' not in response:    
                    response['status'] = False
                    response['status_code'] = 400
                    response['message'] = _(u"Din påmelding er utsatt grunnet prikker.")
                    response['offset'] = postponed_registration_start
            
        print 'response after marks: ',
        print response

        print '------------'

        # Return response if offset was set.
        if 'offset' in response and response['offset'] > timezone.now():
            return response 

        #
        # Offset calculations end
        #

        #Registration not open  
        if timezone.now() < self.attendance_event.registration_start:
            response['message'] = _(u'Påmeldingen har ikke åpnet enda.')
            response['status_code'] = 501 
            return response

        #Room for me on the event?
        if not self.attendance_event.room_on_event:
            response['message'] = _(u"Det er ikke mer plass på dette arrangementet.")
            response['status_code'] = 503 
            return response

        # No objections, set eligible.
        response['status'] = True
        return response

    @property
    def wait_list(self):
        return self.attendance_event.attendees.all()[self.attendance_event.max_capacity:]
        return [] if self.number_of_attendees_on_waiting_list is 0 else self.attendance_event.attendees[self.attendance_event.max_capacity:]

    
    def what_place_is_user_on_wait_list(self, user):
        if self.attendance_event:
            if self.attendance_event.waitlist:
                waitlist = self.wait_list
                if waitlist:
                    for attendee_object in waitlist:
                        if attendee_object.user == user:
                            return list(waitlist).index(attendee_object) + 1
        return 0

    def feedback_mail(self):
        if self.event_type == 1 or self.event_type == 4: #sosialt/utflukt
            return settings.EMAIL_ARRKOM
        elif self.event_type == 2: #Bedpres
            return settings.EMAIL_BEDKOM
        elif self.event_type == 3: #Kurs
            return settings.EMAIL_FAGKOM
        else:
            return settings.DEFAULT_FROM_EMAIL

    @property
    def slug(self):
        return slugify(self.title)    

    @models.permalink
    def get_absolute_url(self):
        return ('events_details', None, {'event_id': self.id, 'event_slug': self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('arrangement')
        verbose_name_plural = _('arrangement')

"""
 BEGIN ACCESS RESTRICTION --------------------------------------------------------------------------
"""


class FieldOfStudyRule(models.Model):
    field_of_study = models.SmallIntegerField(_(u'studieretning'), choices=FIELD_OF_STUDY_CHOICES)
    offset = models.PositiveSmallIntegerField(_(u'utsettelse'), help_text=_(u'utsettelse oppgis i timer')) 

    def get_offset_time(self, time):
        if type(time) is not datetime:
            raise TypeError('time must be a datetime, not %s' % type(arg))
        else:
            return time + timedelta(hours=self.offset)

    def satisfied(self, user, registration_start):
        """ Override method """

        # If the user has the same FOS as this rule    
        if (self.field_of_study == user.field_of_study):
            offset_datetime = self.offset.get_offset_time(registration_start)
            if offset_datetime <= timezone.now():
                return {"status": True, "message": None, "status_code": 210}
            else:
                return {"status": False, "message": _(u"Din studieretning har utsatt påmelding."), "offset": offset_datetime, "status_code": 420}
        return {"status": False, "message": _(u"Din studieretning er en annen enn de som har tilgang til dette arrangementet."), "status_code": 410}

    def __unicode__(self):
        if self.offset.offset > 0:
            time_unit = _(u'timer') if self.offset.offset > 1 else _(u'time')
            return _("%s etter %d %s") % (unicode(self.get_field_of_study_display()), self.offset.offset, time_unit)
        return unicode(self.get_field_of_study_display())


class GradeRule(models.Model):
    grade = models.SmallIntegerField(_(u'klassetrinn'), null=False)
    offset = models.PositiveSmallIntegerField(_(u'utsettelse'), help_text=_(u'utsettelse oppgis i timer')) 

    def get_offset_time(self, time):
        if type(time) is not datetime:
            raise TypeError('time must be a datetime, not %s' % type(arg))
        else:
            return time + timedelta(hours=self.offset)

    def satisfied(self, user, registration_start):
        """ Override method """

        # If the user has the same FOS as this rule    
        if (self.grade == user.year):
            print "WTF"
            offset_datetime = self.offset.get_offset_time(registration_start)
            if offset_datetime <= timezone.now():
                return {"status": True, "message": None, "status_code": 211}
            else:
                return {"status": False, "message": _(u"Ditt klassetrinn har utsatt påmelding."), "offset": offset_datetime, "status_code": 421}
        return {"status": False, "message": _(u"Du er ikke i et klassetrinn som har tilgang til dette arrangementet."), "status_code": 411}

    def __unicode__(self):
        if self.offset.offset > 0:
            time_unit = _(u'timer') if self.offset.offset > 1 else _(u'time')
            return _(u"%s. klasse etter %d %s") % (self.grade, self.offset.offset, time_unit)
        return _(u"%s. klasse") % self.grade


class UserGroupRule(models.Model):
    group = models.ForeignKey(Group, blank=False, null=False)
    offset = models.PositiveSmallIntegerField(_(u'utsettelse'), help_text=_(u'utsettelse oppgis i timer')) 

    def get_offset_time(self, time):
        if type(time) is not datetime:
            raise TypeError('time must be a datetime, not %s' % type(arg))
        else:
            return time + timedelta(hours=self.offset)

    def satisfied(self, user, registration_start):
        """ Override method """
        if self.group in user.groups.all():
            offset_datetime = self.offset.get_offset_time(registration_start)
            if offset_datetime <= timezone.now():
                return {"status": True, "message": None, "status_code": 212}
            else:
                return {"status": False, "message": _(u"%s har utsatt påmelding.") % self.group, "offset": offset_datetime, "status_code": 422}
        return {"status": False, "message": _(u"Du er ikke i en brukergruppe som har tilgang til dette arrangmentet."), "status_code": 412}

    def __unicode__(self):
        if self.offset.offset > 0:
            time_unit = _(u'timer') if self.offset.offset > 1 else _(u'time')
            return _(u"%s etter %d %s") % (unicode(self.group), self.offset.offset, time_unit)
        return unicode(self.group)


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

        if self.grade_rules:
            for grade_rule in self.grade_rules.all():
                response = grade_rule.satisfied(user, registration_start)
                if response['status']:
                    return response
                else:
                    errors.append(response)

        if self.field_of_study_rules:
            for fos_rule in self.field_of_study_rules.all():
                response = fos_rule.satisfied(user, registration_start)
                if response['status']:
                    return response
                else:
                    errors.append(response)

        if self.user_group_rules:
            for user_group_rule in self.user_group_rules.all():
                response = user_group_rule.satisfied(user, registration_start)
                if response['status']:
                    return response
                else:
                    errors.append(response)
        
        # If we found errors, check if there was any that just had an offset. Then find the 
        # largest one so we can show the user when he will be eligible to register.
        if errors:
            # Offsets are returned as datetime objects. We compare them initially to a date 
            # before registration_start.
            smallest_offset = registration_start - timedelta(days=1)
            current_response = {}

            for error in errors:
                if 'offset' in error:
                    if error['offset'] < smallest_offset:
                        smallest_offset = error['offset']
                        current_response = error
            return current_response or errors[0]

    def __unicode__(self):
        return self.description



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

    max_capacity = models.PositiveIntegerField(_(u'maks-kapasitet'), null=False, blank=False)
    waitlist = models.BooleanField(_(u'venteliste'), default=False)
    registration_start = models.DateTimeField(_(u'registrerings-start'), null=False, blank=False)
    registration_end = models.DateTimeField(_(u'registrerings-slutt'), null=False, blank=False)

    #Access rules
    rule_bundles = models.ManyToManyField(RuleBundle, blank=True, null=True)

    @property
    def room_on_event(self):
        return True if (self.attendees.count() < self.max_capacity) or self.waitlist else False

    @property
    def will_i_be_on_wait_list(self):
        return True if (self.attendees.count() >= self.max_capacity) and self.waitlist else False

    @property
    def waitlist_enabled(self):
        return self.waitlist

    def rules_satisfied(self, user):
        """
        Checks a user against rules applied to an attendance event
        """
        # If there are no rule_bundles on this object, all members of Online are allowed.
        if not self.rule_bundles.exists() and user.is_member:
            return {'status': True, 'status_code': 200}

        smallest_offset = self.registration_start 
        errors = []    

        # Check all rule bundles
        # If one satisfies, return true, else check offset or append to response
        for rule_bundle in self.rule_bundles.all():
            response =  rule_bundle.satisfied(user, self.registration_start)
            if response['status']:
                return response
            elif 'offset' in response:
                if response['offset'] < smallest_offset:
                    smallest_offset = response['offset']
                    status_object = response
            else:
                errors.append(response)
        
        if smallest_offset > self.registration_start:
            return status_object
        if errors:
            return errors[0]

        # If there are no rule bundles and the user is not a member, return False
        return {'status': False, 'message': _(u"Dette arrangementet er kun åpent for medlemmer."), 'status_code': 400}

    def is_attendee(self, user):
        return self.attendees.filter(user=user)

    def __unicode__(self):
        return self.event.title

    class Meta:
        verbose_name = _(u'påmelding')
        verbose_name_plural = _(u'påmeldinger')

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
        unique_together = (('event', 'user'),)


# Registrations for watson indexing
watson.register(Event)
