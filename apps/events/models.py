# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from random import choice as random_choice
from typing import List, Tuple

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.core import validators
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import SET_NULL, Case, Q, Value, When
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from guardian.shortcuts import assign_perm
from unidecode import unidecode

from apps.authentication.constants import FieldOfStudyType
from apps.authentication.models import OnlineGroup
from apps.companyprofile.models import Company
from apps.events.constants import EventType, RegisterStatus
from apps.events.exceptions import RegisterException
from apps.feedback.models import FeedbackRelation
from apps.gallery.models import ResponsiveImage
from apps.marks.models import get_expiration_date
from apps.payment import status as payment_status

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL

# Managers


class EventOrderedByRegistration(models.Manager):
    """
    Order events by registration start if registration start is within 7 days of today.
    """

    def get_queryset(self):
        now = timezone.now()
        DELTA_FUTURE_SETTING = settings.OW4_SETTINGS.get("events").get(
            "FEATURED_DAYS_FUTURE"
        )
        DELTA_PAST_SETTING = settings.OW4_SETTINGS.get("events").get(
            "FEATURED_DAYS_PAST"
        )
        DAYS_BACK_DELTA = timezone.now() - timedelta(days=DELTA_PAST_SETTING)
        DAYS_FORWARD_DELTA = timezone.now() + timedelta(days=DELTA_FUTURE_SETTING)

        return (
            super(EventOrderedByRegistration, self)
            .get_queryset()
            .annotate(
                registration_filtered=Case(
                    When(
                        Q(event_end__gte=now)
                        & Q(attendance_event__registration_start__gte=DAYS_BACK_DELTA)
                        & Q(
                            attendance_event__registration_start__lte=DAYS_FORWARD_DELTA
                        ),
                        then="attendance_event__registration_start",
                    ),
                    default="event_end",
                    output_field=models.DateTimeField(),
                )
            )
            .annotate(
                is_today=Case(
                    When(event_end__date=now.date(), then=Value(1)),
                    default=Value(0),
                    output_field=models.IntegerField(),
                )
            )
            .order_by("-is_today", "registration_filtered")
        )

    def get_queryset_for_user(self, user: User):
        """
        :return: Queryset filtered by these requirements:
            event is visible AND (event has NO group restriction OR user having access to restricted event)
            OR the user is attending the event themselves
        """
        group_restriction_query = Q(group_restriction__isnull=True) | Q(
            group_restriction__groups__in=user.groups.all()
        )
        is_attending_query = (
            (
                Q(attendance_event__isnull=False)
                & Q(attendance_event__attendees__user=user)
            )
            if not user.is_anonymous
            else Q()
        )
        is_visible_query = Q(visible=True)
        return (
            self.get_queryset()
            .filter(group_restriction_query & is_visible_query | is_attending_query)
            .distinct()
        )


class Event(models.Model):
    """
    Base class for Event-objects.
    """

    IMAGE_FOLDER = "images/events"
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".gif", ".png", ".tif", ".tiff"]

    # Managers
    objects = models.Manager()
    by_registration = EventOrderedByRegistration()

    author = models.ForeignKey(
        User,
        related_name="created_events",
        verbose_name=_("Oppretter"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    title = models.CharField(_("tittel"), max_length=60)
    """Event title"""
    event_start = models.DateTimeField(_("start-dato"))
    """Datetime for event start"""
    event_end = models.DateTimeField(_("slutt-dato"))
    """Datetime for event end"""
    location = models.CharField(_("lokasjon"), max_length=100)
    """Event location"""
    ingress_short = models.CharField(
        _("kort ingress"),
        max_length=150,
        validators=[validators.MinLengthValidator(25)],
        help_text="En kort ingress som blir vist på forsiden",
    )
    """Short ingress used on the frontpage"""
    ingress = models.TextField(
        _("ingress"),
        validators=[validators.MinLengthValidator(25)],
        help_text="En ingress som blir vist før beskrivelsen.",
    )
    """Ingress used in archive and details page"""
    description = models.TextField(
        _("beskrivelse"), validators=[validators.MinLengthValidator(45)]
    )
    """Event description shown on details page"""
    image = models.ForeignKey(
        ResponsiveImage,
        related_name="events",
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    """Event image"""
    event_type = models.SmallIntegerField(
        _("type"), choices=EventType.ALL_CHOICES, null=False
    )
    """Event type. Used mainly for filtering"""
    organizer = models.ForeignKey(
        Group, verbose_name=_("arrangør"), blank=True, null=True, on_delete=SET_NULL
    )
    """Committee responsible for organizing the event"""
    visible = models.BooleanField(
        _("Vis arrangementet utenfor Dashboard og Adminpanelet"),
        default=True,
        help_text=_("Denne brukes for å skjule eksisterende arrangementer."),
    )
    companies = models.ManyToManyField(
        to=Company,
        verbose_name=_("Bedrifter"),
        related_name="events",
        through="CompanyEvent",
    )

    feedback = GenericRelation(FeedbackRelation)

    def is_attendance_event(self):
        """ Returns true if the event is an attendance event """
        return hasattr(self, "attendance_event")

    # TODO move payment and feedback stuff to attendance event when dasboard is done

    def feedback_users(self):
        if self.is_attendance_event():
            return [
                a.user for a in self.attendance_event.attendees.filter(attended=True)
            ]
        return []

    def feedback_date(self):
        return self.event_end

    def feedback_title(self):
        return self.title

    def feedback_info(self):
        info = OrderedDict()
        if self.is_attendance_event():
            info[_("Påmeldte")] = self.attendance_event.number_of_attendees
            info[_("Oppmøtte")] = self.attendance_event.number_of_attendees - len(
                self.attendance_event.not_attended()
            )
            info[_("Venteliste")] = self.attendance_event.number_on_waitlist

        return info

    @property
    def images(self):
        images = ResponsiveImage.objects.none()
        if self.image:
            images |= ResponsiveImage.objects.filter(pk=self.image.id)
        company_image_ids = self.companies.values_list("image")
        images |= ResponsiveImage.objects.filter(pk__in=company_image_ids)
        return images.distinct()

    @property
    def company_event(self):
        return CompanyEvent.objects.filter(event=self)

    @property
    def organizer_name(self):
        return self.organizer.name

    def feedback_mail(self):
        """
        Get feedback mail from organizer Online group.
        Use default from email if the organizer group does not have configured an email.
        """
        if self.organizer:
            organizer_group = OnlineGroup.objects.filter(pk=self.organizer.id).first()
            if organizer_group and organizer_group.email:
                return organizer_group.email

        return settings.DEFAULT_FROM_EMAIL

    def can_display(self, user):
        restriction = GroupRestriction.objects.filter(event=self).first()
        if (
            not user.is_anonymous
            and self.is_attendance_event()
            and self.attendance_event.is_attendee(user)
        ):
            return True
        if not self.visible:
            return False
        if not restriction:
            return True
        if not user:
            return False
        return restriction.has_access(user)

    @property
    def slug(self):
        return slugify(unidecode(self.title))

    def get_absolute_url(self):
        return reverse(
            "events_details", kwargs={"event_id": self.id, "event_slug": self.slug}
        )

    def clean(self):
        if not self.organizer:
            raise ValidationError({"organizer": ["Arrangementet krever en arrangør."]})

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.organizer:
            assign_perm("events.change_event", self.organizer, obj=self)
            assign_perm("events.delete_event", self.organizer, obj=self)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("arrangement")
        verbose_name_plural = _("arrangementer")
        permissions = (("view_event", "View Event"),)
        default_permissions = ("add", "change", "delete")


"""
 BEGIN ACCESS RESTRICTION --------------------------------------------------------------------------
"""


class Rule(models.Model):
    """
    Super class for a rule object
    """

    success_status = RegisterStatus.ALLOWED_GENERIC_RULE
    not_opened_status = RegisterStatus.BLOCKED_NOT_OPEN_YET
    delayed_signup_status = RegisterStatus.POSTPONED_GENERIC_RULE
    not_satisfied_status = RegisterStatus.BLOCKED_GENERIC_RULE

    offset = models.PositiveSmallIntegerField(
        _("utsettelse"), help_text=_("utsettelse oppgis i timer"), default=0
    )

    def get_offset_time(self, time: timezone.datetime):
        if type(time) is not datetime:
            raise TypeError("time must be a datetime, not %s" % type(time))
        else:
            return time + timedelta(hours=self.offset)

    def satisfies_constraint(self, user: User) -> bool:
        return True

    def satisfied(
        self, user: User, registration_start: timezone.datetime
    ) -> Tuple[RegisterStatus, timedelta]:
        """ Override method """

        if self.satisfies_constraint(user):
            offset_datetime = self.get_offset_time(registration_start)
            # If the offset is in the past, it means you can attend even with the offset
            if offset_datetime < timezone.now():
                return self.success_status, timedelta(hours=0)
            # If there is no offset, the signup just hasn't started yet
            elif self.offset == 0:
                return self.not_opened_status, timedelta(hours=0)
            # In the last case there is a delayed signup
            else:
                return self.delayed_signup_status, timedelta(hours=self.offset)
        return self.not_satisfied_status, timedelta(hours=0)

    def __str__(self):
        return "Rule"

    class Meta:
        permissions = (("view_rule", "View Rule"),)
        default_permissions = ("add", "change", "delete")


class FieldOfStudyRule(Rule):
    success_status = RegisterStatus.ALLOWED_FOS_RULE
    delayed_signup_status = RegisterStatus.POSTPONED_FOS_RULE
    not_satisfied_status = RegisterStatus.BLOCKED_FOS_RULE

    field_of_study = models.SmallIntegerField(
        _("studieretning"), choices=FieldOfStudyType.ALL_CHOICES
    )

    def satisfies_constraint(self, user: User) -> bool:
        return self.field_of_study == user.field_of_study

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s etter %d %s") % (
                str(self.get_field_of_study_display()),
                self.offset,
                time_unit,
            )
        return str(self.get_field_of_study_display())

    class Meta:
        permissions = (("view_fieldofstudyrule", "View FieldOfStudyRule"),)
        default_permissions = ("add", "change", "delete")


class GradeRule(Rule):
    success_status = RegisterStatus.ALLOWED_GRADE_RULE
    delayed_signup_status = RegisterStatus.POSTPONED_GRADE_RULE
    not_satisfied_status = RegisterStatus.BLOCKED_GRADE_RULE

    grade = models.SmallIntegerField(_("klassetrinn"), null=False)

    def satisfies_constraint(self, user: User) -> bool:
        return self.grade == user.year

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s. klasse etter %d %s") % (self.grade, self.offset, time_unit)
        return _("%s. klasse") % self.grade

    class Meta:
        permissions = (("view_graderule", "View GradeRule"),)
        default_permissions = ("add", "change", "delete")


class UserGroupRule(Rule):
    success_status = RegisterStatus.ALLOWED_GROUP_RULE
    delayed_signup_status = RegisterStatus.POSTPONED_GROUP_RULE
    not_satisfied_status = RegisterStatus.BLOCKED_GROUP_RULE

    group = models.ForeignKey(Group, blank=False, null=False, on_delete=models.CASCADE)

    def satisfies_constraint(self, user: User) -> bool:
        return self.group in user.groups.all()

    def __str__(self):
        if self.offset > 0:
            time_unit = _("timer") if self.offset > 1 else _("time")
            return _("%s etter %d %s") % (str(self.group), self.offset, time_unit)
        return str(self.group)

    class Meta:
        permissions = (("view_usergrouprule", "View UserGroupRule"),)
        default_permissions = ("add", "change", "delete")


class RuleBundle(models.Model):
    """
    Access restriction rule object
    """

    description = models.CharField(
        _("beskrivelse"), max_length=100, blank=True, null=True
    )
    field_of_study_rules = models.ManyToManyField(FieldOfStudyRule, blank=True)
    grade_rules = models.ManyToManyField(GradeRule, blank=True)
    user_group_rules = models.ManyToManyField(UserGroupRule, blank=True)

    def get_all_rules(self):
        rules: List[Rule] = []
        rules.extend(self.field_of_study_rules.all())
        rules.extend(self.grade_rules.all())
        rules.extend(self.user_group_rules.all())
        return rules

    @property
    def rule_strings(self):
        return [str(rule) for rule in self.get_all_rules()]

    def satisfied(
        self, user, registration_start
    ) -> List[Tuple[RegisterStatus, timedelta]]:
        all_statuses: List[Tuple[RegisterStatus, timedelta]] = []

        for rule in self.get_all_rules():
            status, offset = rule.satisfied(user, registration_start)
            # Return early if any of the responses is allowed for register.
            # We won't have to care about the rest since we know the user can register.
            if RegisterStatus.is_allowed(status):
                return [(status, offset)]

            all_statuses.append((status, offset))

        return all_statuses

    def get_minimum_offset_for_user(self, user: User):
        offsets = [
            rule.offset
            for rule in self.get_all_rules()
            if rule.satisfies_constraint(user)
        ]
        if len(offsets) == 0:
            return timezone.timedelta(hours=0)
        offsets.sort()
        return timezone.timedelta(hours=offsets[0])

    def __str__(self):
        if self.description:
            return self.description
        elif self.rule_strings:
            return ", ".join(self.rule_strings)
        else:
            return _("Tom rule bundle.")

    class Meta:
        permissions = (("view_rulebundle", "View RuleBundle"),)
        default_permissions = ("add", "change", "delete")


"""
 END ACCESS RESTRICTION --------------------------------------------------------------------------
"""


class Extras(models.Model):
    """
    Choices for events
    """

    choice = models.CharField("valg", max_length=69)
    note = models.CharField("notat", max_length=200, blank=True, null=True)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _("ekstra valg")
        verbose_name_plural = _("ekstra valg")
        ordering = ["choice"]
        default_permissions = ("add", "change", "delete")


class AttendanceEvent(models.Model):
    """
    Events that require special considerations regarding attendance.
    """

    event = models.OneToOneField(
        Event,
        primary_key=True,
        related_name="attendance_event",
        on_delete=models.CASCADE,
    )
    max_capacity = models.PositiveIntegerField(
        _("maks-kapasitet"), null=False, blank=False
    )
    waitlist = models.BooleanField(_("venteliste"), default=False)
    guest_attendance = models.BooleanField(
        _("gjestepåmelding"), null=False, blank=False, default=False
    )
    registration_start = models.DateTimeField(
        _("registrerings-start"), null=False, blank=False
    )
    unattend_deadline = models.DateTimeField(
        _("avmeldings-frist"), null=False, blank=False
    )
    registration_end = models.DateTimeField(
        _("registrerings-slutt"), null=False, blank=False
    )

    # Automatic mark setting for not attending
    automatically_set_marks = models.BooleanField(
        _("automatisk prikk"),
        default=False,
        help_text=_("Påmeldte som ikke har møtt vil automatisk få prikk"),
    )
    marks_has_been_set = models.BooleanField(default=False)

    # Access rules
    rule_bundles = models.ManyToManyField(RuleBundle, blank=True)

    # Extra choices
    extras = models.ManyToManyField(Extras, blank=True)

    payments = GenericRelation("payment.Payment")

    @property
    def id(self):
        """ Proxy Event id """
        return self.event_id

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
        return hasattr(self, "reserved_seats")

    @property
    def has_extras(self):
        return self.extras.exists()

    @property
    def attending_attendees_qs(self):
        """Queryset with all attendees not on waiting list """
        return self.attendees.all()[: self.number_of_attendee_seats]

    def not_attended(self):
        """List of all attending attendees who have not attended"""
        return [a.user for a in self.attending_attendees_qs if not a.attended]

    @property
    def waitlist_qs(self):
        """Queryset with all attendees on waiting list """
        return self.attendees.all()[self.number_of_attendee_seats :]

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
        return (
            0
            if self.number_of_seats_taken == self.max_capacity
            else self.max_capacity - self.number_of_seats_taken
        )

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
        dyr = [
            "piggsvin",
            "kjøttmeis",
            "flaggermus",
            "elg",
            "villsvin",
            "rådyr",
            "moskus",
            "narhval",
            "spekkhogger",
            "gaupe",
            "ekorn",
            "kanin",
            "lemen",
            "neshorn",
            "ørn",
            "gullfisk",
            "kodiakbjørn",
            "hacker",
            "stol",
            "bever",
            "datamaskin",
            "piano",
            "strykejern",
            "samurai",
            "laks",
            "server",
        ]

        visible_attendees = []
        for attendee in self.attending_attendees_qs:
            user = attendee.user
            visible = attendee.show_as_attending_event
            f_name, l_name = (
                [user.first_name, user.last_name]
                if visible
                else ["Anonym " + random_choice(dyr), ""]
            )
            year = "{} klasse".format(user.year)
            visible_attendees.append(
                {
                    "visible": visible,
                    "first_name": f_name,
                    "last_name": l_name,
                    "year": year,
                }
            )

        return sorted(
            visible_attendees, key=lambda attendee: attendee["visible"], reverse=True
        )

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
            if (
                not suspension.expiration_date
                or suspension.expiration_date > timezone.now().date()
            ):
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
        from apps.events.utils import (
            handle_waitlist_bump,
        )  # Imported here to avoid circular import

        if not self.waitlist_qs:
            return
        bumped_attendees = self.waitlist_qs[:extra_capacity]
        handle_waitlist_bump(self.event, bumped_attendees, self.payment())

    def _check_signup(self, user: User):
        # User is already an attendee
        if self.is_attendee(user):
            raise RegisterException(status=RegisterStatus.BLOCKED_IS_ATTENDING)

        # Registration closed
        if timezone.now() > self.registration_end:
            raise RegisterException(status=RegisterStatus.ERROR_REGISTRATION_CLOSED)

        # Room for me on the event?
        if not self.room_on_event:
            raise RegisterException(status=RegisterStatus.ERROR_NO_SEATS_LEFT)

        # Registration not open
        if timezone.now() < self.registration_start:
            raise RegisterException(status=RegisterStatus.BLOCKED_NOT_OPEN_YET)

        # Is suspended
        if self.is_suspended(user):
            raise RegisterException(status=RegisterStatus.BLOCKED_SUSPENSION)

        # Checks if the event is group restricted and if the user is in the right group
        if not self.event.can_display(user):
            raise RegisterException(status=RegisterStatus.BLOCKED_NO_ACCESS)

    def build_status_response(self, status: RegisterStatus):
        return {
            "status": RegisterStatus.is_allowed(status),
            "status_code": status.value,
            "message": status.label,
        }

    def is_eligible_for_signup(self, user: User):
        """
        Checks if a user can attend a specific event
        """
        try:
            self._check_signup(user)
            self._check_marks(user)
            # Are there any rules preventing me from attending?
            # This should be checked last of the offsets, because it can completely deny you access.
            status = self.rules_satisfied(user)
            if status:
                return self.build_status_response(status)

            # Base case is allowing all members
            return self.build_status_response(RegisterStatus.ALLOWED_MEMBERS)

        except RegisterException as register_exception:
            return self.build_status_response(register_exception.status)

    def get_minimum_rule_offset_for_user(self, user: User):
        offsets_deltas = [
            rule_bundle.get_minimum_offset_for_user(user)
            for rule_bundle in self.rule_bundles.all()
        ]
        if len(offsets_deltas) == 0:
            return timezone.timedelta(hours=0)
        offsets_deltas.sort()
        return offsets_deltas[0]

    def get_minimum_offset_for_user(self, user: User):
        minimum_user_offset = self.get_minimum_rule_offset_for_user(user)
        mark_expiry_date = get_expiration_date(user)
        if mark_expiry_date and mark_expiry_date > timezone.now().date():
            # Offset is currently 1 day if you have marks, regardless of amount.
            mark_offset = timedelta(days=1)
            minimum_user_offset += mark_offset

        return minimum_user_offset

    def _check_marks(self, user: User):
        expiry_date = get_expiration_date(user)
        if expiry_date and expiry_date > timezone.now().date():
            # Offset is currently 1 day if you have marks, regardless of amount.
            mark_offset = timedelta(days=1)
            rule_offset = self.get_minimum_rule_offset_for_user(user)

            previous_offset = self.registration_start + rule_offset
            postponed_registration_start = previous_offset + mark_offset

            logger.debug(self.registration_start)
            logger.debug(postponed_registration_start)
            logger.debug(rule_offset)

            before_expiry = self.registration_start.date() < expiry_date

            if postponed_registration_start > timezone.now() and before_expiry:
                if (
                    previous_offset < postponed_registration_start
                    or previous_offset == self.registration_start
                ):
                    raise RegisterException(
                        status=RegisterStatus.BLOCKED_MARK,
                        offset=postponed_registration_start,
                    )

    def _process_rulebundle_satisfaction_responses(self, user: User):
        # Obtain status for every rule in every rule bundle for the event
        statuses: List[Tuple[RegisterStatus, timedelta]] = []
        for rule_bundle in self.rule_bundles.all():
            bundle_statuses = rule_bundle.satisfied(user, self.registration_start)
            statuses.extend(bundle_statuses)

        postponed_statuses: List[Tuple[RegisterStatus, timedelta]] = []
        blocked_statuses: List[RegisterStatus] = []
        error_statuses: List[RegisterStatus] = []

        for status, offset in statuses:
            # Return early if any status allows the user to register
            if RegisterStatus.is_allowed(status):
                return status
            # If registration is not open no users will be able to register anyways
            if status == RegisterStatus.BLOCKED_NOT_OPEN_YET:
                raise RegisterException(status=RegisterStatus.BLOCKED_NOT_OPEN_YET)
            if RegisterStatus.is_postponed(status):
                postponed_statuses.append((status, offset))
            if RegisterStatus.is_blocked(status):
                error_statuses.append(status)

        if len(postponed_statuses) > 0:
            # TODO: Get the actual least offset one
            least_offset_status, offset = postponed_statuses[0]
            raise RegisterException(status=least_offset_status)
        if len(blocked_statuses) > 0:
            raise RegisterException(status=blocked_statuses[0])
        if len(error_statuses) > 0:
            raise RegisterException(status=error_statuses[0])

    def rules_satisfied(self, user: User) -> RegisterStatus:
        """
        Checks a user against rules applied to an attendance event
        """
        # If the event has guest attendance, allow absolutely anyone
        if self.guest_attendance:
            return RegisterStatus.ALLOWED_GUEST

        # Without guest attendance the user has to be a member to attend
        if not user.is_member:
            raise RegisterException(status=RegisterStatus.BLOCKED_MEMBERS_ONLY)

        # If there are no rule_bundles on this object, all members of Online are allowed.
        if not self.rule_bundles.exists() and user.is_member:
            return RegisterStatus.ALLOWED_MEMBERS

        return self._process_rulebundle_satisfaction_responses(user)

    def is_attendee(self, user):
        return self.attendees.filter(user=user).exists()

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
            logger.warning(
                "Multiple payment objects connected to attendance event #%s." % self.pk
            )
            return (
                self.get_payments()
            )  # Sneaky hack, however, use get_payments for multiple

    def __str__(self):
        return self.event.title

    def bump_waitlist(self):
        """
        Checks if any attendees should be bumped from the waitlist

        Waitlist bumping can happen if e.g. max capacity or number of reserved seats is adjusted
        This method should be called with edited fields, but before the attendance event is saved
        as it looks at the difference between the fields.
        """

        old_attendance_event = AttendanceEvent.objects.filter(
            event_id=self.event_id
        ).first()
        if not old_attendance_event:
            # Attendance event was just created
            return

        extra_capacity = (
            self.number_of_attendee_seats
            - old_attendance_event.number_of_attendee_seats
        )
        if extra_capacity > 0:
            # Using old object because waitlist has already been changed in self
            old_attendance_event.bump_waitlist_for_x_users(extra_capacity)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.bump_waitlist()

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.event.organizer:
            assign_perm("events.change_attendanceevent", self.event.organizer, obj=self)
            assign_perm("events.delete_attendanceevent", self.event.organizer, obj=self)

    class Meta:
        verbose_name = _("påmelding")
        verbose_name_plural = _("påmeldinger")
        permissions = (("view_attendanceevent", "View AttendanceEvent"),)
        default_permissions = ("add", "change", "delete")


class CompanyEvent(models.Model):
    """
    Company relation to AttendanceEvent
    """

    company = models.ForeignKey(
        Company, verbose_name=_("bedrifter"), on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        verbose_name=_("arrangement"),
        related_name="company_events",
        on_delete=models.CASCADE,
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.event.organizer:
            assign_perm("events.change_companyevent", self.event.organizer, obj=self)
            assign_perm("events.delete_companyevent", self.event.organizer, obj=self)

    class Meta:
        verbose_name = _("bedrift")
        verbose_name_plural = _("bedrifter")
        permissions = (("view_companyevent", "View CompanyEvent"),)
        ordering = ("company",)
        default_permissions = ("add", "change", "delete")
        unique_together = (("company", "event"),)


class Attendee(models.Model):
    """
    User relation to AttendanceEvent.
    """

    event = models.ForeignKey(
        AttendanceEvent, related_name="attendees", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    attended = models.BooleanField(_("var tilstede"), default=False)
    paid = models.BooleanField(_("har betalt"), default=False)
    note = models.CharField(_("notat"), max_length=100, blank=True, default="")
    extras = models.ForeignKey(Extras, blank=True, null=True, on_delete=models.CASCADE)

    show_as_attending_event = models.BooleanField(
        _("vis som påmeldt arrangementet"), default=False
    )
    allow_pictures = models.BooleanField(_("greit å ta bilde"), default=False)

    def __str__(self):
        return self.user.get_full_name()

    def delete(self):
        # Importing here to prevent circular dependencies
        from apps.payment.models import PaymentDelay

        try:
            PaymentDelay.objects.get(
                user=self.user, payment=self.event.payment()
            ).delete()
        except PaymentDelay.DoesNotExist:
            # Do nothing
            False

        if not self.is_on_waitlist():
            self.event.bump_waitlist_for_x_users()

        super(Attendee, self).delete()

    @property
    def payment_relations(self):
        # Importing here to prevent circular dependencies
        from apps.payment.models import PaymentRelation

        payment = self.event.payment()
        if payment:
            payment_relations = PaymentRelation.objects.filter(
                payment=payment, user=self.user
            )
            return payment_relations
        return None

    @property
    def has_paid(self):
        """
        Useful for checking if the user has paid, and if anything potentially needs refunding.
        :return: If the user has paid anything for the event.
        """
        if self.payment_relations:
            non_refunded_payment_relations = self.payment_relations.filter(
                refunded=False
            )
            return any(
                map(
                    lambda relation: relation.status == payment_status.DONE,
                    non_refunded_payment_relations,
                )
            )
        return False

    @property
    def payment_delays(self):
        # Importing here to prevent circular dependencies
        from apps.payment.models import PaymentDelay

        try:
            return PaymentDelay.objects.filter(
                user=self.user, payment=self.event.payment()
            )
        except PaymentDelay.DoesNotExist:
            return PaymentDelay.objects.none()

    def get_payment_deadline(self):
        delays = self.payment_delays
        if len(delays) == 0:
            return "Betalt"
        return delays.first().valid_to

    def is_on_waitlist(self):
        return self in self.event.waitlist_qs

    # Unattend user from event
    def unattend(self, admin_user):
        logger.info(
            'User %s was removed from event "%s" by %s on %s'
            % (self.user.get_full_name(), self.event, admin_user, datetime.now())
        )

        # Notify responsible group if someone is unattended after deadline
        if timezone.now() >= self.event.unattend_deadline:
            subject = "[%s] %s har blitt avmeldt arrangementet av %s" % (
                self.event,
                self.user.get_full_name(),
                admin_user,
            )

            content = render_to_string(
                "events/email/unattend.txt",
                {
                    "user": self.user.get_full_name(),
                    "user_id": self.user_id,
                    "event": self.event,
                    "admin": admin_user,
                    "admin_id": admin_user.id,
                    "time": timezone.now().strftime("%d. %b %H:%M:%S"),
                },
            )

            to_email = self.event.event.feedback_mail()
            EmailMessage(subject, content, "online@online.ntnu.no", [to_email]).send()

        if not self.has_paid:
            self._clean_payment_delays()

        # TODO: Not delete attendee unless payments have been refunded?
        self.delete()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.event.event.organizer:
            assign_perm("events.change_attendee", self.event.event.organizer, obj=self)
            assign_perm("events.delete_attendee", self.event.event.organizer, obj=self)

    def _clean_payment_delays(self):
        for delay in self.payment_delays:
            delay.delete()

    class Meta:
        ordering = ["timestamp"]
        unique_together = (("event", "user"),)
        permissions = (("view_attendee", "View Attendee"),)
        default_permissions = ("add", "change", "delete")


class Reservation(models.Model):
    attendance_event = models.OneToOneField(
        AttendanceEvent, related_name="reserved_seats", on_delete=models.CASCADE
    )
    seats = models.PositiveIntegerField("reserverte plasser", blank=False, null=False)

    @property
    def number_of_seats_taken(self):
        return self.reservees.count()

    def __str__(self):
        return "Reservasjoner for %s" % self.attendance_event.event.title

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # Notify attendance event that the waitlist may have changed
        self.attendance_event.bump_waitlist()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.attendance_event.event.organizer:
            assign_perm(
                "events.change_reservation",
                self.attendance_event.event.organizer,
                obj=self,
            )
            assign_perm(
                "events.delete_reservation",
                self.attendance_event.event.organizer,
                obj=self,
            )

    class Meta:
        verbose_name = _("reservasjon")
        verbose_name_plural = _("reservasjoner")
        permissions = (("view_reservation", "View Reservation"),)
        default_permissions = ("add", "change", "delete")


class Reservee(models.Model):
    """
    Reservation entry
    """

    reservation = models.ForeignKey(
        Reservation, related_name="reservees", on_delete=models.CASCADE
    )
    # I 2014 var norges lengste navn på 69 tegn;
    # julius andreas gimli arn macgyver chewbacka highlander elessar-jankov
    name = models.CharField("navn", max_length=69)
    note = models.CharField("notat", max_length=100)
    allergies = models.CharField("allergier", max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.reservation.attendance_event.event.organizer:
            assign_perm(
                "events.change_reservee",
                self.reservation.attendance_event.event.organizer,
                obj=self,
            )
            assign_perm(
                "events.delete_reservee",
                self.reservation.attendance_event.event.organizer,
                obj=self,
            )

    class Meta:
        verbose_name = _("reservasjon")
        verbose_name_plural = _("reservasjoner")
        ordering = ["id"]
        permissions = (("view_reservee", "View Reservee"),)
        default_permissions = ("add", "change", "delete")


class GroupRestriction(models.Model):
    event = models.OneToOneField(
        Event,
        primary_key=True,
        related_name="group_restriction",
        on_delete=models.CASCADE,
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_("Legg til de gruppene som skal ha tilgang til arrangementet"),
    )

    def has_access(self, user):
        # returns True if any of the users groups are in one of the accepted groups
        return self.groups.filter(id__in=user.groups.all()).exists()

    class Meta:
        verbose_name = _("restriksjon")
        verbose_name_plural = _("restriksjoner")
        permissions = (("view_restriction", "View Restriction"),)
        default_permissions = ("add", "change", "delete")
