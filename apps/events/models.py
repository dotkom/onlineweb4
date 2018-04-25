# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, timedelta
from random import choice as random_choice

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.core import validators
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import SET_NULL, Case, Q, Value, When
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext as _
from guardian.shortcuts import assign_perm
from unidecode import unidecode

from apps.authentication.models import FIELD_OF_STUDY_CHOICES
from apps.companyprofile.models import Company
from apps.feedback.models import FeedbackRelation
from apps.gallery.models import ResponsiveImage
from apps.marks.models import get_expiration_date

User = settings.AUTH_USER_MODEL

TYPE_CHOICES = (
    (1, 'Sosialt'),
    (2, 'Bedriftspresentasjon'),
    (3, 'Kurs'),
    (4, 'Utflukt'),
    (5, 'Ekskursjon'),
    (6, 'Internt'),
    (7, 'Annet'),
)


# Managers

class EventOrderedByRegistration(models.Manager):
    """
    Order events by registration start if registration start is within 7 days of today.
    """
    def get_queryset(self):
        now = timezone.now()
        DELTA_FUTURE_SETTING = settings.OW4_SETTINGS.get('events').get('FEATURED_DAYS_FUTURE')
        DELTA_PAST_SETTING = settings.OW4_SETTINGS.get('events').get('FEATURED_DAYS_PAST')
        DAYS_BACK_DELTA = timezone.now() - timedelta(days=DELTA_PAST_SETTING)
        DAYS_FORWARD_DELTA = timezone.now() + timedelta(days=DELTA_FUTURE_SETTING)

        return super(EventOrderedByRegistration, self).get_queryset().\
            annotate(registration_filtered=Case(
                When(Q(event_end__gte=now) &
                     Q(attendance_event__registration_start__gte=DAYS_BACK_DELTA) &
                     Q(attendance_event__registration_start__lte=DAYS_FORWARD_DELTA),
                     then='attendance_event__registration_start'),
                default='event_end',
                output_field=models.DateTimeField()
            )
        ).annotate(is_today=Case(
            When(event_end__date=now.date(),
                 then=Value(1)),
            default=Value(0),
            output_field=models.IntegerField()
        )
        ).order_by('-is_today', 'registration_filtered')


class Event(models.Model):
    """
    Base class for Event-objects.
    """

    IMAGE_FOLDER = "images/events"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    # Managers
    objects = models.Manager()
    by_registration = EventOrderedByRegistration()

    author = models.ForeignKey(User, related_name='oppretter', null=True, blank=True)
    title = models.CharField(_('tittel'), max_length=60)
    """Event title"""
    event_start = models.DateTimeField(_('start-dato'))
    """Datetime for event start"""
    event_end = models.DateTimeField(_('slutt-dato'))
    """Datetime for event end"""
    location = models.CharField(_('lokasjon'), max_length=100)
    """Event location"""
    ingress_short = models.CharField(_("kort ingress"), max_length=150,
                                     validators=[validators.MinLengthValidator(25)],
                                     help_text='En kort ingress som blir vist på forsiden')
    """Short ingress used on the frontpage"""
    ingress = models.TextField(_('ingress'), validators=[validators.MinLengthValidator(25)],
                               help_text='En ingress som blir vist før beskrivelsen.')
    """Ingress used in archive and details page"""
    description = models.TextField(_('beskrivelse'), validators=[validators.MinLengthValidator(45)])
    """Event description shown on details page"""
    image = models.ForeignKey(ResponsiveImage, related_name='events', blank=True, null=True, on_delete=SET_NULL)
    """Event image"""
    event_type = models.SmallIntegerField(_('type'), choices=TYPE_CHOICES, null=False)
    """Event type. Used mainly for filtering"""
    organizer = models.ForeignKey(Group, verbose_name=_('arrangør'), blank=True, null=True, on_delete=SET_NULL)
    """Committee responsible for organizing the event"""

    feedback = GenericRelation(FeedbackRelation)

    def is_attendance_event(self):
        """ Returns true if the event is an attendance event """
        return hasattr(self, 'attendance_event')

    # TODO move payment and feedback stuff to attendance event when dasboard is done

    def feedback_users(self):
        if self.is_attendance_event():
            return [a.user for a in self.attendance_event.attendees.filter(attended=True)]
        return []

    def feedback_date(self):
        return self.event_end

    def feedback_title(self):
        return self.title

    def feedback_info(self):
        info = OrderedDict()
        if self.is_attendance_event():
            info[_('Påmeldte')] = self.attendance_event.number_of_attendees
            info[_('Oppmøtte')] = self.attendance_event.number_of_attendees - len(self.attendance_event.not_attended())
            info[_('Venteliste')] = self.attendance_event.number_on_waitlist

        return info

    @property
    def company_event(self):
        return CompanyEvent.objects.filter(event=self)

    def feedback_mail(self):
        if self.event_type == 1 or self.event_type == 4:  # Sosialt & Utflukt
            return settings.EMAIL_ARRKOM
        elif self.event_type == 2:  # Bedpres
            return settings.EMAIL_BEDKOM
        elif self.event_type == 3:  # Kurs
            return settings.EMAIL_FAGKOM
        elif self.event_type == 5:  # Ekskursjon
            return settings.EMAIL_EKSKOM
        else:
            return settings.DEFAULT_FROM_EMAIL

    def can_display(self, user):
        restriction = GroupRestriction.objects.filter(event=self).first()
        if not restriction:
            return True
        if not user:
            return False
        return restriction.has_access(user)

    @property
    def slug(self):
        return slugify(unidecode(self.title))

    @models.permalink
    def get_absolute_url(self):
        return 'events_details', None, {'event_id': self.id, 'event_slug': self.slug}

    def clean(self):
        if not self.organizer:
            raise ValidationError({'organizer': ['Arrangementet krever en arrangør.']})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.organizer:
            assign_perm('events.change_event', self.organizer, obj=self)
            assign_perm('events.delete_event', self.organizer, obj=self)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('arrangement')
        verbose_name_plural = _('arrangementer')
        permissions = (
            ('view_event', 'View Event'),
        )


"""
 BEGIN ACCESS RESTRICTION --------------------------------------------------------------------------
"""


class Rule(models.Model):
    """
    Super class for a rule object
    """
    offset = models.PositiveSmallIntegerField(_('utsettelse'), help_text=_('utsettelse oppgis i timer'), default=0)

    def get_offset_time(self, time):
        if type(time) is not datetime:
            raise TypeError('time must be a datetime, not %s' % type(time))
        else:
            return time + timedelta(hours=self.offset)

    def satisfied(self, user):
        """ Checks if a user satisfies the rules """
        return True

    def __str__(self):
        return 'Rule'

    class Meta:
        permissions = (
            ('view_rule', 'View Rule'),
        )


class FieldOfStudyRule(Rule):
    field_of_study = models.SmallIntegerField(_('studieretning'), choices=FIELD_OF_STUDY_CHOICES)

    def satisfied(self, user, registration_start):
        """ Override method """

        # If the user has the same FOS as this rule
        if self.field_of_study == user.field_of_study:
            offset_datetime = self.get_offset_time(registration_start)
            # If the offset is in the past, it means you can attend even with the offset
            if offset_datetime < timezone.now():
                return {"status": True, "message": None, "status_code": 210}
            # If there is no offset, the signup just hasn't started yet
            elif self.offset == 0:
                return {"status": False, "message": _("Påmeldingen har ikke åpnet enda."), "status_code": 402}
            # In the last case there is a delayed signup
            else:
                return {"status": False, "message": _("Din studieretning har utsatt påmelding."),
                        "offset": offset_datetime, "status_code": 420}
        return {
            "status": False, "message":
            _("Din studieretning er en annen enn de som har tilgang til dette arrangementet."), "status_code": 410}

    def __str__(self):
        if self.offset > 0:
            time_unit = _('timer') if self.offset > 1 else _('time')
            return _("%s etter %d %s") % (str(self.get_field_of_study_display()), self.offset, time_unit)
        return str(self.get_field_of_study_display())

    class Meta:
        permissions = (
            ('view_fieldofstudyrule', 'View FieldOfStudyRule'),
        )


class GradeRule(Rule):
    grade = models.SmallIntegerField(_('klassetrinn'), null=False)

    def satisfied(self, user, registration_start):
        """ Override method """

        # If the user has the same FOS as this rule
        if self.grade == user.year:
            offset_datetime = self.get_offset_time(registration_start)
            # If the offset is in the past, it means you can attend even with the offset
            if offset_datetime < timezone.now():
                return {"status": True, "message": None, "status_code": 211}
            # If there is no offset, the signup just hasn't started yet
            elif self.offset == 0:
                return {"status": False, "message": _("Påmeldingen har ikke åpnet enda."), "status_code": 402}
            # In the last case there is a delayed signup
            else:
                return {
                    "status": False, "message":
                    _("Ditt klassetrinn har utsatt påmelding."), "offset": offset_datetime, "status_code": 421}
        return {
            "status": False, "message":
                _("Ditt klassetrinn har ikke tilgang til dette arrangementet."), "status_code": 411}

    def __str__(self):
        if self.offset > 0:
            time_unit = _('timer') if self.offset > 1 else _('time')
            return _("%s. klasse etter %d %s") % (self.grade, self.offset, time_unit)
        return _("%s. klasse") % self.grade

    class Meta:
        permissions = (
            ('view_graderule', 'View GradeRule'),
        )


class UserGroupRule(Rule):
    group = models.ForeignKey(Group, blank=False, null=False)

    def satisfied(self, user, registration_start):
        """ Override method """
        if self.group in user.groups.all():
            offset_datetime = self.get_offset_time(registration_start)
            # If the offset is in the past, it means you can attend even with the offset
            if offset_datetime < timezone.now():
                return {"status": True, "message": None, "status_code": 212}
            # If there is no offset, the signup just hasn't started yet
            elif self.offset == 0:
                return {"status": False, "message": _("Påmeldingen er ikke åpnet enda."), "status_code": 402}
            # In the last case there is a delayed signup
            else:
                return {"status": False, "message": _("%s har utsatt påmelding.") % self.group,
                        "offset": offset_datetime, "status_code": 422}
        return {
            "status": False, "message":
            _("Din brukergruppe har ikke tilgang til dette arrangementet."), "status_code": 412}

    def __str__(self):
        if self.offset > 0:
            time_unit = _('timer') if self.offset > 1 else _('time')
            return _("%s etter %d %s") % (str(self.group), self.offset, time_unit)
        return str(self.group)

    class Meta:
        permissions = (
            ('view_usergrouprule', 'View UserGroupRule'),
        )


class RuleBundle(models.Model):
    """
    Access restriction rule object
    """
    description = models.CharField(_('beskrivelse'), max_length=100, blank=True, null=True)
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, blank=True)
    user_group_rules = models.ManyToManyField(UserGroupRule, blank=True)

    def get_all_rules(self):
        rules = []
        rules.extend(self.field_of_study_rules.all())
        rules.extend(self.grade_rules.all())
        rules.extend(self.user_group_rules.all())
        return rules

    def get_rule_strings(self):
        return [str(rule) for rule in self.get_all_rules()]

    def satisfied(self, user, registration_start):

        errors = []

        for rule in self.get_all_rules():
            response = rule.satisfied(user, registration_start)
            if response['status']:
                return [response]
            else:
                errors.append(response)

        return errors

    def __str__(self):
        if self.description:
            return self.description
        elif self.get_rule_strings():
            return ", ".join(self.get_rule_strings())
        else:
            return _("Tom rule bundle.")

    class Meta:
        permissions = (
            ('view_rulebundle', 'View RuleBundle'),
        )


"""
 END ACCESS RESTRICTION --------------------------------------------------------------------------
"""


class Extras(models.Model):
    """
    Choices for events
    """

    choice = models.CharField('valg', max_length=69)
    note = models.CharField('notat', max_length=200, blank=True, null=True)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _("ekstra valg")
        verbose_name_plural = _("ekstra valg")
        ordering = ['choice']


class AttendanceEvent(models.Model):
    """
    Events that require special considerations regarding attendance.
    """
    event = models.OneToOneField(
        Event,
        primary_key=True,
        related_name='attendance_event')

    max_capacity = models.PositiveIntegerField(_('maks-kapasitet'), null=False, blank=False)
    waitlist = models.BooleanField(_('venteliste'), default=False)
    guest_attendance = models.BooleanField(_('gjestepåmelding'), null=False, blank=False, default=False)
    registration_start = models.DateTimeField(_('registrerings-start'), null=False, blank=False)
    unattend_deadline = models.DateTimeField(_('avmeldings-frist'), null=False, blank=False)
    registration_end = models.DateTimeField(_('registrerings-slutt'), null=False, blank=False)

    # Automatic mark setting for not attending
    automatically_set_marks = models.BooleanField(_('automatisk prikk'), default=False,
                                                  help_text=_('Påmeldte som ikke har møtt vil automatisk få prikk'))
    marks_has_been_set = models.BooleanField(default=False)

    # Access rules
    rule_bundles = models.ManyToManyField(RuleBundle, blank=True)

    # Extra choices
    extras = models.ManyToManyField(Extras, blank=True)

    payments = GenericRelation('payment.Payment')

    @property
    def feedback(self):
        """Proxy for generic feedback relation on event"""
        return self.event.feedback

    def get_feedback(self):
        return self.feedback.first()

    def has_feedback(self):
        return self.feedback.exists()

    @property
    def has_reservation(self):
        """Returns whether this event has an attached reservation """
        return hasattr(self, 'reserved_seats')

    @property
    def has_extras(self):
        return self.extras.exists()

    @property
    def attending_attendees_qs(self):
        """Queryset with all attendees not on waiting list """
        return self.attendees.all()[:self.number_of_attendee_seats]

    def not_attended(self):
        """List of all attending attendees who have not attended"""
        return [a.user for a in self.attending_attendees_qs if not a.attended]

    @property
    def waitlist_qs(self):
        """Queryset with all attendees on waiting list """
        return self.attendees.all()[self.number_of_attendee_seats:]

    @property
    def reservees_qs(self):
        """Queryset with all reserved seats which have been filled """
        if self.has_reservation:
            return self.reserved_seats.reservees.all()
        return []

    @property
    def attendees_not_paid(self):
        """List of attendees who haven't paid"""
        return list(self.attendees.filter(paid=False))

    @property
    def number_of_attendees(self):
        """ Count of all attendees not in waiting list """
        # We need to use len() instead of .count() here, because of the prefetched event archive
        return len(self.attending_attendees_qs)

    @property
    def number_on_waitlist(self):
        """ Count of all attendees on waiting list """
        # We need to use len() instead of .count() here, because of the prefetched event archive
        return len(self.waitlist_qs)

    @property
    def number_of_attendee_seats(self):
        """Return the number of seats which can be used for attendees"""
        return self.max_capacity - self.number_of_reserved_seats

    @property
    def number_of_reserved_seats(self):
        """Total number of seats for this event that are reserved"""
        return self.reserved_seats.seats if self.has_reservation else 0

    @property
    def number_of_reserved_seats_taken(self):
        """Returns number of reserved seats which have been filled"""
        return self.reserved_seats.number_of_seats_taken if self.has_reservation else 0

    @property
    def number_of_seats_taken(self):
        """Returns the total amount of taken seats for an attendance_event."""
        # This includes all attendees + reserved seats for the event, if any.
        # Always use the total number of reserved seats here, because they are not
        # available for regular users to claim.
        return self.number_of_attendees + self.number_of_reserved_seats

    @property
    def free_seats(self):
        """Integer representing the number of free seats for an event"""
        return 0 if self.number_of_seats_taken == self.max_capacity else self.max_capacity - self.number_of_seats_taken

    @property
    def room_on_event(self):
        """Returns True if there are free seats or an open waiting list"""
        return True if self.free_seats > 0 or self.waitlist else False

    @property
    def registration_open(self):
        return timezone.now() < self.registration_start

    @property
    def visible_attending_attendees(self):
        """ List with all attendees whom want to be displayed as attending else return a anonymous name """
        dyr = ['piggsvin', 'kjøttmeis', 'flaggermus', 'elg', 'villsvin', 'rådyr', 'moskus', 'narhval',
               'spekkhogger', 'gaupe', 'ekorn', 'kanin', 'lemen', 'neshorn', 'ørn', 'gullfisk', 'kodiakbjørn',
               'hacker', 'stol', 'bever', 'datamaskin', 'piano', 'strykejern', 'samurai', 'laks', 'server']

        visible_attendees = []
        for attendee in self.attending_attendees_qs:
            user = attendee.user
            visible = attendee.show_as_attending_event
            f_name, l_name = [user.first_name, user.last_name] if visible else ['Anonym ' + random_choice(dyr), '']
            year = '{} klasse'.format(user.year)
            visible_attendees.append({'visible': visible, 'first_name': f_name, 'last_name': l_name, 'year': year})

        return sorted(visible_attendees, key=lambda attendee: attendee['visible'], reverse=True)

    def has_delayed_signup(self, user):
        pass

    def is_marked(self, user):
        expiry_date = get_expiration_date(user)
        return expiry_date and expiry_date > timezone.now().date()

    def has_postponed_registration(self, user):
        if not self.is_marked(user):
            return False
        expiry_date = get_expiration_date(user)
        mark_offset = timedelta(days=1)
        postponed_registration_start = self.registration_start + mark_offset

        before_expiry = self.registration_start.date() < expiry_date

        if postponed_registration_start > timezone.now() and before_expiry:
            return postponed_registration_start

    def is_suspended(self, user):
        for suspension in user.get_active_suspensions():
            if not suspension.expiration_date or suspension.expiration_date > timezone.now().date():
                return True

        return False

    @property
    def will_i_be_on_wait_list(self):
        return True if self.free_seats == 0 and self.waitlist else False

    @property
    def waitlist_enabled(self):
        return self.waitlist

    def bump_waitlist_for_x_users(self, extra_capacity=1):
        """Handle bumping of the x first users on the waitlist"""
        from apps.events.utils import handle_waitlist_bump  # Imported here to avoid circular import
        if not self.waitlist_qs:
            return
        bumped_attendees = self.waitlist_qs[:extra_capacity]
        handle_waitlist_bump(self.event, bumped_attendees, self.payment())

    def is_eligible_for_signup(self, user):
        """
        Checks if a user can attend a specific event
        This method checks for:
        - Already attended
        - Waitlist
        - Room on event
        - Rules
        - Marks
        - Suspension
        @param User object
        The returned dict contains a key called 'status_code'. These codes follow the HTTP
        standard in terms of overlying scheme.
        2XX = successful
        4XX = client error (user related)
        5XX = server error (event related)
        These codes are meant as a debugging tool only. The eligibility checking is quite
        extensive, and tracking where it's going wrong is much needed.
        """

        response = {'status': False, 'message': '', 'status_code': None}

        # User is already an attendee
        if self.attendees.filter(user=user).exists():
            response['message'] = 'Du er allerede meldt på dette arrangementet.'
            response['status_code'] = 404
            return response

        # Registration closed
        if timezone.now() > self.registration_end:
            response['message'] = _('Påmeldingen er ikke lenger åpen.')
            response['status_code'] = 502
            return response

        # Room for me on the event?
        if not self.room_on_event:
            response['message'] = _("Det er ikke mer plass på dette arrangementet.")
            response['status_code'] = 503
            return response

        #
        # Offset calculations.
        #

        # Are there any rules preventing me from attending?
        # This should be checked last of the offsets, because it can completely deny you access.
        response = self.rules_satisfied(user)
        if not response['status']:
            if 'offset' not in response:
                return response

        # Do I have any marks that postpone my registration date?
        response = self._check_marks(response, user)

        # Return response if offset was set.
        if 'offset' in response and response['offset'] > timezone.now():
            return response

        #
        # Offset calculations end
        #

        # Registration not open
        if timezone.now() < self.registration_start:
            response['status'] = False
            response['message'] = _('Påmeldingen har ikke åpnet enda.')
            response['status_code'] = 501
            return response

        # Is suspended
        if self.is_suspended(user):
            response['status'] = False
            response['message'] = _("Du er suspandert og kan ikke melde deg på.")
            response['status_code'] = 402

            return response

        # Checks if the event is group restricted and if the user is in the right group
        if not self.event.can_display(user):
            response['status'] = False
            response['message'] = _("Du har ikke tilgang til å melde deg på dette arrangementet.")
            response['status_code'] = 403

            return response

        # No objections, set eligible.
        response['status'] = True
        return response

    def _check_marks(self, response, user):
        expiry_date = get_expiration_date(user)
        if expiry_date and expiry_date > timezone.now().date():
            # Offset is currently 1 day if you have marks, regardless of amount.
            mark_offset = timedelta(days=1)
            postponed_registration_start = self.registration_start + mark_offset

            before_expiry = self.registration_start.date() < expiry_date

            if postponed_registration_start > timezone.now() and before_expiry:
                if 'offset' in response and response['offset'] < postponed_registration_start \
                        or 'offset' not in response:
                    response['status'] = False
                    response['status_code'] = 401
                    response['message'] = _("Din påmelding er utsatt grunnet prikker.")
                    response['offset'] = postponed_registration_start
        return response

    def _process_rulebundle_satisfaction_responses(self, responses):
        # Put the smallest offset faaar into the future.
        smallest_offset = timezone.now() + timedelta(days=365)
        offset_response = {}
        future_response = {}
        errors = []

        for response in responses:
            if response['status']:
                return response
            elif 'offset' in response:
                if response['offset'] < smallest_offset:
                    smallest_offset = response['offset']
                    offset_response = response
            elif response['status_code'] == 402:
                future_response = response
            else:
                errors.append(response)

        if future_response:
            return future_response
        if smallest_offset > timezone.now() and offset_response:
            return offset_response
        if errors:
            return errors[0]

    def rules_satisfied(self, user):
        """
        Checks a user against rules applied to an attendance event
        """
        # If the event has guest attendance, allow absolutely anyone
        if self.guest_attendance:
            return {'status': True, 'status_code': 201}

        # If the user is not a member, return False right away
        # TODO check for guest list
        if not user.is_member:
            return {
                'status': False, 'message':
                _("Dette arrangementet er kun åpent for medlemmer."), 'status_code': 400}

        # If there are no rule_bundles on this object, all members of Online are allowed.
        if not self.rule_bundles.exists() and user.is_member:
            return {'status': True, 'status_code': 200}

        # Check all rule bundles
        responses = []

        # If one satisfies, return true, else append to the error list
        for rule_bundle in self.rule_bundles.all():
            responses.extend(rule_bundle.satisfied(user, self.registration_start))

        return self._process_rulebundle_satisfaction_responses(responses)

    def is_attendee(self, user):
        return self.attendees.filter(user=user)

    def is_on_waitlist(self, user):
        return any(a.user == user for a in self.waitlist_qs)

    def what_place_is_user_on_wait_list(self, user):
        if self.waitlist:
            waitlist = self.waitlist_qs
            if waitlist:
                for attendee_object in waitlist:
                    if attendee_object.user == user:
                        return list(waitlist).index(attendee_object) + 1
        return 0

    def payment(self):
        try:
            return self.payments.get()
        except ObjectDoesNotExist:
            return None

    def get_payments(self):
        return self.payments.all()

    def get_payment(self):
        try:
            return self.payments.get()
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            import logging
            logger = logging.getLogger(__name__)
            logger.warn("Multiple payment objects connected to attendance event #%s." % self.pk)
            return self.get_payments()  # Sneaky hack, however, use get_payments for multiple

    def __str__(self):
        return self.event.title

    def bump_waitlist(self):
        """
        Checks if any attendees should be bumped from the waitlist

        Waitlist bumping can happen if e.g. max capacity or number of reserved seats is adjusted
        This method should be called with edited fields, but before the attendance event is saved
        as it looks at the difference between the fields.
        """

        old_attendance_event = AttendanceEvent.objects.filter(event_id=self.event_id).first()
        if not old_attendance_event:
            # Attendance event was just created
            return

        extra_capacity = self.number_of_attendee_seats - old_attendance_event.number_of_attendee_seats
        if extra_capacity > 0:
            # Using old object because waitlist has already been changed in self
            old_attendance_event.bump_waitlist_for_x_users(extra_capacity)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.bump_waitlist()

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.event.organizer:
            assign_perm('events.change_attendanceevent', self.event.organizer, obj=self)
            assign_perm('events.delete_attendanceevent', self.event.organizer, obj=self)

    class Meta:
        verbose_name = _('påmelding')
        verbose_name_plural = _('påmeldinger')
        permissions = (
            ('view_attendanceevent', 'View AttendanceEvent'),
        )


class CompanyEvent(models.Model):
    """
    Company relation to AttendanceEvent
    """
    company = models.ForeignKey(Company, verbose_name=_('bedrifter'))
    event = models.ForeignKey(Event, verbose_name=_('arrangement'), related_name='companies')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.event.organizer:
            assign_perm('events.change_companyevent', self.event.organizer, obj=self)
            assign_perm('events.delete_companyevent', self.event.organizer, obj=self)

    class Meta:
        verbose_name = _('bedrift')
        verbose_name_plural = _('bedrifter')
        permissions = (
            ('view_companyevent', 'View CompanyEvent'),
        )
        ordering = ('company',)


class Attendee(models.Model):
    """
    User relation to AttendanceEvent.
    """
    event = models.ForeignKey(AttendanceEvent, related_name="attendees")
    user = models.ForeignKey(User)

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    attended = models.BooleanField(_('var tilstede'), default=False)
    paid = models.BooleanField(_('har betalt'), default=False)
    note = models.CharField(_('notat'), max_length=100, blank=True, default='')
    extras = models.ForeignKey(Extras, blank=True, null=True)

    show_as_attending_event = models.BooleanField(_('vis som påmeldt arrangementet'), default=False)

    def __str__(self):
        return self.user.get_full_name()

    def delete(self):
        # Importing here to prevent circular dependencies
        from apps.payment.models import PaymentDelay
        try:
            PaymentDelay.objects.filter(user=self.user, payment=self.event.payment()).delete()
        except PaymentDelay.DoesNotExist:
            # Do nothing
            False

        if not self.is_on_waitlist():
            self.event.bump_waitlist_for_x_users()

        super(Attendee, self).delete()

    def is_on_waitlist(self):
        return self in self.event.waitlist_qs

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.event.event.organizer:
            assign_perm('events.change_attendee', self.event.event.organizer, obj=self)
            assign_perm('events.delete_attendee', self.event.event.organizer, obj=self)

    class Meta:
        ordering = ['timestamp']
        unique_together = (('event', 'user'),)
        permissions = (
            ('view_attendee', 'View Attendee'),
        )


class Reservation(models.Model):
    attendance_event = models.OneToOneField(AttendanceEvent, related_name="reserved_seats")
    seats = models.PositiveIntegerField("reserverte plasser", blank=False, null=False)

    @property
    def number_of_seats_taken(self):
        return self.reservees.count()

    def __str__(self):
        return "Reservasjoner for %s" % self.attendance_event.event.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Notify attendance event that the waitlist may have changed
        self.attendance_event.bump_waitlist()
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.attendance_event.event.organizer:
            assign_perm('events.change_reservation', self.attendance_event.event.organizer, obj=self)
            assign_perm('events.delete_reservation', self.attendance_event.event.organizer, obj=self)

    class Meta:
        verbose_name = _("reservasjon")
        verbose_name_plural = _("reservasjoner")
        permissions = (
            ('view_reservation', 'View Reservation'),
        )


class Reservee(models.Model):
    """
    Reservation entry
    """
    reservation = models.ForeignKey(Reservation, related_name='reservees')
    # I 2014 var norges lengste navn på 69 tegn;
    # julius andreas gimli arn macgyver chewbacka highlander elessar-jankov
    name = models.CharField('navn', max_length=69)
    note = models.CharField('notat', max_length=100)
    allergies = models.CharField('allergier', max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

        if self.reservation.attendance_event.event.organizer:
            assign_perm('events.change_reservee', self.reservation.attendance_event.event.organizer, obj=self)
            assign_perm('events.delete_reservee', self.reservation.attendance_event.event.organizer, obj=self)

    class Meta:
        verbose_name = _("reservasjon")
        verbose_name_plural = _("reservasjoner")
        ordering = ['id']
        permissions = (
            ('view_reservee', 'View Reservee'),
        )


class GroupRestriction(models.Model):
    event = models.OneToOneField(
        Event,
        primary_key=True,
        related_name='group_restriction')

    groups = models.ManyToManyField(Group, blank=True,
                                    help_text=_('Legg til de gruppene som skal ha tilgang til arrangementet'))

    def has_access(self, user):
        # returns True if any of the users groups are in one of the accepted groups
        return self.groups.filter(id__in=user.groups.all()).exists()

    class Meta:
        verbose_name = _("restriksjon")
        verbose_name_plural = _("restriksjoner")
        permissions = (
            ('view_restriction', 'View Restriction'),
        )
