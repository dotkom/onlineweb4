import logging
from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import SET_NULL, Case, F, Q, Value, When
from django.db.models.functions import TruncSecond
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from guardian.shortcuts import assign_perm
from unidecode import unidecode

from apps.authentication.models import OnlineGroup
from apps.companyprofile.models import Company
from apps.events.constants import EventType
from apps.feedback.models import FeedbackRelation
from apps.gallery.models import ResponsiveImage

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL

# Managers


class EventOrderedByClosestActiveThenNewestInactive(models.Manager):
    """
    Order by closest event to start if not yet started, then all others are ordered by last ended.
    """

    def get_queryset(self):
        now = timezone.now()

        return (
            super()
            .get_queryset()
            .annotate(
                closest=Case(
                    When(
                        Q(event_start__gte=now) & Q(event_end__gte=now),
                        then="event_start",
                    ),
                    default=now + (now - TruncSecond(F("event_end"))),  # Don't even ask
                    output_field=models.DateTimeField(),
                )
            )
            .annotate(
                has_passed=Case(
                    When(
                        Q(event_end__lte=now),
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=models.BooleanField(),
                )
            )
            .order_by("has_passed", "closest")
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
            super()
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


# Store all actions users take in regards to events.
class EventUserAction(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    type = models.CharField(
        max_length=15,
        choices=[
            ("register", "register"),
            ("unregister", "unregister"),
            #  , ("pay", "pay"), ("chose_extra", "chose_extra"), ("sent_feedback", "sent_feedback") TODO: these should be added, but we start with register/unregister for now.
        ],
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
    by_nearest_active_event = EventOrderedByClosestActiveThenNewestInactive()

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
        validators=[validators.MinLengthValidator(1)],
        help_text="En kort ingress som blir vist på forsiden",
    )
    """Short ingress used on the frontpage"""
    ingress = models.TextField(
        _("ingress"),
        validators=[validators.MinLengthValidator(1)],
        help_text="En ingress som blir vist før beskrivelsen.",
    )
    """Ingress used in archive and details page"""
    description = models.TextField(
        _("beskrivelse"), validators=[validators.MinLengthValidator(1)]
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
        _("type"), choices=EventType.choices, null=False
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
        through="events.CompanyEvent",
    )

    feedback = GenericRelation(FeedbackRelation)

    def is_attendance_event(self):
        """Returns true if the event is an attendance event"""
        return hasattr(self, "attendance_event")

    # TODO move payment and feedback stuff to attendance event when dasboard is done

    def feedback_users(self):
        # why is this not on attendance_event?
        from .Attendance import Attendee

        if self.is_attendance_event():
            qs = self.attendance_event.attendees.filter(attended=True)
        else:
            qs = Attendee.objects.none()
        from apps.authentication.models import OnlineUser as User

        return User.objects.filter(pk__in=qs.values_list("user", flat=True))

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
        # we want to have self.image first, so use dict-keys instead of set since keys are ordered.
        # it is not entirely clear why we even need to de-deplicate here
        images = {self.image: None}
        images |= {c.image: None for c in self.companies.select_related("image")}
        # if company or we are missing an image, remove it
        try:
            del images[None]
        except KeyError:
            pass
        return list(images.keys())

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
        from .Attendance import GroupRestriction

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
        if self.event_end < self.event_start:
            raise ValidationError({"event_end": ["Event må starte før det kan slutte"]})
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
