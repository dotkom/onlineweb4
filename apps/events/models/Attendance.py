from dataclasses import dataclass
from datetime import UTC, datetime
from random import choice as random_choice

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from guardian.shortcuts import assign_perm

from apps.authentication.models import OnlineGroup
from apps.companyprofile.models import Company
from apps.marks.models import (
    MarkDelay,
    Suspended,
    user_sanctions,
)
from apps.payment import status as payment_status
from apps.payment.mixins import PaymentMixin

from .Event import User, logger
from .Extras import Extras


class StatusCode(models.IntegerChoices):
    """
    These codes follow the HTTP standard in terms of overlying scheme.
    2XX = successful
    4XX = client error (user related)
    5XX = server error (event related)
    These codes are meant as a debugging tool only. The eligibility checking is quite
    extensive, and tracking where it's going wrong is much needed.
    """

    # Event has no rulebundles
    SUCCESS_MEMBER = 200, _("Du kan melde deg på.")
    SUCCESS_GUEST_SIGNUP = 201, _("Du kan melde deg på.")

    SUCCESS_FIELD_OF_STUDY = 210, _("Du kan melde deg på.")
    SUCCESS_GRADE = 211, _("Du kan melde deg på.")
    SUCCESS_USER_GROUP = 212, _("Du kan melde deg på.")
    SUCCESS_UNKNOWN = 213, _("Du kan melde deg på.")

    NOT_A_MEMBER = 400, _("Arrangementet er kun åpnet for medlemmer av Online.")
    DELAYED_SIGNUP_MARKS = 401, _("Din påmelding er utsatt grunnet prikker.")
    DELAYED_ACCESS = 402, _("Din påmelding er utsatt.")
    ACCESS_DENIED = 403, _("Du har ikke adgang til dette arrangementet.")
    ALREADY_SIGNED_UP = 404, _("Du er allerede påmeldt.")
    SUSPENDED = 405, _("Du er suspendert, og kan derfor ikke melde deg på.")

    NOT_SATISFIED_FIELD_OF_STUDY = (
        410,
        _("Din studieretning har ikke adgang til dette arrangementet."),
    )
    NOT_SATISFIED_GRADE = (
        411,
        _("Din studieretning har ikke adgang til dette arrangementet."),
    )
    NOT_SATISFIED_USER_GROUP = (
        412,
        _("Din studieretning har ikke adgang til dette arrangementet."),
    )
    NOT_SATISFIED_UNKNOWN = (
        413,
        _("Din studieretning har ikke adgang til dette arrangementet."),
    )

    DELAYED_SIGNUP_FIELD_OF_STUDY = 420, _("Din påmelding er utsatt.")
    DELAYED_SIGNUP_GRADE = 421, _("Din påmelding er utsatt.")
    DELAYED_SIGNUP_USER_GROUP = 422, _("Din påmelding er utsatt.")
    DELAYED_SIGNUP_UNKNOWN = 423, _("Din påmelding er utsatt.")

    NOT_SATISFIED = 500, _("Du oppfyller ikke reglene for å melde deg på.")
    SIGNUP_NOT_OPENED_YET = 501, _("Påmeldingen har ikke åpnet enda.")
    SIGNUP_CLOSED = 502, _("Påmeldingen er ikke lenger åpen.")
    NO_SEATS_LEFT = 503, _("Det er ikke flere plasser igjen.")

    @property
    def is_success(self):
        return 200 <= self < 300

    @property
    def message(self):
        return self.label


@dataclass
class AttendanceResult:
    status_code: StatusCode
    # If the attendee has a postponed admission, this is the new start time
    offset: timezone.datetime | None = None

    @property
    def status(self) -> bool:
        """eligibility or wheter the user has signed up"""
        return self.status_code.is_success

    @property
    def message(self) -> str:
        """User-facing message"""
        return self.status_code.message


class AttendanceEvent(PaymentMixin, models.Model):
    """
    Events that require special considerations regarding attendance.
    """

    event = models.OneToOneField(
        "Event",
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
    rule_bundles = models.ManyToManyField("RuleBundle", blank=True)

    # Extra choices
    extras = models.ManyToManyField(Extras, blank=True)

    payments = GenericRelation("payment.Payment")

    @property
    def id(self):
        """Proxy Event id"""
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
        """Returns whether this event has an attached reservation"""
        return hasattr(self, "reserved_seats")

    @property
    def has_extras(self):
        return self.extras.exists()

    @property
    def attending_attendees_qs(self):
        """Queryset with all attendees not on waiting list"""
        return self.attendees.all()[: self.number_of_attendee_seats]

    def not_attended(self):
        """List of all attending attendees who have not attended"""
        return [a.user for a in self.attending_attendees_qs if not a.attended]

    @property
    def waitlist_qs(self):
        """Queryset with all attendees on waiting list"""
        return self.attendees.all()[self.number_of_attendee_seats :]

    @property
    def reservees_qs(self):
        """Queryset with all reserved seats which have been filled"""
        if self.has_reservation:
            return self.reserved_seats.reservees.all()
        return []

    @property
    def attendees_not_paid(self):
        """List of attendees who haven't paid"""
        return list(self.attendees.filter(paid=False))

    @property
    def number_of_attendees(self):
        """Count of all attendees not in waiting list"""
        # We need to use len() instead of .count() here, because of the prefetched event archive
        return len(self.attending_attendees_qs)

    @property
    def number_on_waitlist(self):
        """Count of all attendees on waiting list"""
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
        """List with all attendees whom want to be displayed as attending else return a anonymous name"""
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
            year = f"{user.year} klasse"
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

    @property
    def will_i_be_on_wait_list(self):
        return True if self.free_seats == 0 and self.waitlist else False

    @property
    def waitlist_enabled(self):
        return self.waitlist

    def bump_waitlist_for_x_users(self, extra_capacity=1):
        """Handle bumping of the x first users on the waitlist"""
        # Imported here to avoid circular import
        from apps.events.utils import handle_waitlist_bump

        if not self.waitlist_qs:
            return
        bumped_attendees = self.waitlist_qs[:extra_capacity]
        handle_waitlist_bump(self.event, bumped_attendees, self.payment())

    def is_eligible_for_signup(
        self, user: User, now: datetime | None = None
    ) -> AttendanceResult:
        """
        Checks if a user can attend a specific event
        This method checks for:
        - Already attended
        - Waitlist
        - Room on event
        - Rules
        - Marks
        - Suspension
        """
        if now is None:
            now = timezone.now()
        # User is already an attendee
        if self.attendees.filter(user=user).exists():
            return AttendanceResult(StatusCode.ALREADY_SIGNED_UP)

        if now > self.registration_end:
            return AttendanceResult(StatusCode.SIGNUP_CLOSED)

        if now < self.registration_start:
            return AttendanceResult(StatusCode.SIGNUP_NOT_OPENED_YET)

        if not self.room_on_event:
            return AttendanceResult(StatusCode.NO_SEATS_LEFT)

        # Checks if the event is group restricted and if the user is in the right group
        if not self.event.can_display(user):
            return AttendanceResult(StatusCode.ACCESS_DENIED)

        # Are there any rules preventing me from attending?
        # This should be checked last of the offsets, because it can completely deny you access.
        response = self.rules_satisfied(user)

        if not response.status and response.offset is None:
            return response

        match user_sanctions(user, max(self.registration_start, now).date()):
            case Suspended():
                return AttendanceResult(StatusCode.SUSPENDED)
            case MarkDelay(delay):
                curr_start = response.offset or self.registration_start
                new_reg_start = curr_start + delay

                if now < new_reg_start:
                    return AttendanceResult(
                        StatusCode.DELAYED_SIGNUP_MARKS,
                        new_reg_start,
                    )
            case None:
                pass

        return response

    def rules_satisfied(self, user: User) -> AttendanceResult:
        """
        Checks a user against rules applied to an attendance event
        """
        # If the event has guest attendance, allow absolutely anyone
        if self.guest_attendance:
            return AttendanceResult(StatusCode.SUCCESS_GUEST_SIGNUP)

        # TODO check for guest list
        if not user.is_member:
            return AttendanceResult(StatusCode.NOT_A_MEMBER)

        # If there are no rule_bundles on this object, all members of Online are allowed.
        if not self.rule_bundles.exists() and user.is_member:
            return AttendanceResult(StatusCode.SUCCESS_MEMBER)

        # Check all rule bundles
        responses: list[AttendanceResult] = [
            result
            for rb in self.rule_bundles.all()
            for result in rb.satisfied(user, self.registration_start)
        ]

        min_offset: None | AttendanceResult = None
        for r in responses:
            if r.status:
                return r

            if min_offset is not None:
                min_offset = min(
                    min_offset,
                    r,
                    key=lambda x: x.offset or datetime.max.replace(tzinfo=UTC),
                )
            else:
                min_offset = r

        return min_offset

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
                f"Multiple payment objects connected to attendance event #{self.pk}."
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

    def get_payment_description(self):
        return self.event.title

    def get_payment_email(self):
        organizer = self.event.organizer
        organizer_group: OnlineGroup = OnlineGroup.objects.filter(
            group=organizer
        ).first()
        if organizer_group and organizer_group.email:
            return organizer_group.email
        else:
            return settings.DEFAULT_FROM_EMAIL

    def is_user_allowed_to_pay(self, user: User):
        """
        In the case of attendance events the user should only be allowed to pay if they are attending
        and has not paid yet.
        """
        is_attending = self.is_attendee(user)
        if is_attending:
            attendee = Attendee.objects.get(user=user, event=self)
            return not attendee.has_paid
        return False

    def can_refund_payment(self, payment_relation) -> tuple[bool, str]:
        if self.unattend_deadline < timezone.now():
            return False, _("Fristen for å melde seg av har utgått")
        if len(Attendee.objects.filter(event=self, user=payment_relation.user)) == 0:
            return False, _("Du er ikke påmeldt dette arrangementet.")
        if self.event.event_start < timezone.now():
            return False, _("Dette arrangementet har allerede startet.")

        return True, ""

    def on_payment_done(self, user: User):
        attendee = Attendee.objects.filter(event=self, user=user)

        if attendee:
            attendee[0].paid = True
            attendee[0].save()
        else:
            Attendee.objects.create(event=self, user=user, paid=True)

    def on_payment_refunded(self, payment_relation):
        Attendee.objects.get(event=self, user=payment_relation.user).delete()

    def get_payment_receipt_items(self, payment_relation) -> list[dict]:
        items = [
            {
                "name": self.get_payment_description(),
                "price": payment_relation.payment_price.price,
                "quantity": 1,
            }
        ]
        return items

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
        ordering = ("pk",)


class CompanyEvent(models.Model):
    """
    Company relation to AttendanceEvent
    """

    company = models.ForeignKey(
        Company, verbose_name=_("bedrifter"), on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        "Event",
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

        if not self.event.image and self.company.image:
            self.event.image = self.company.image
            self.event.save()

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

    def delete(self, **kwargs):
        # Importing here to prevent circular dependencies
        from apps.payment.models import PaymentDelay

        try:
            PaymentDelay.objects.get(
                user=self.user, payment=self.event.payment()
            ).delete()
        except PaymentDelay.DoesNotExist:
            # Do nothing
            pass

        if not self.is_on_waitlist():
            self.event.bump_waitlist_for_x_users()

        super().delete(**kwargs)

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
                relation.status == payment_status.DONE
                for relation in non_refunded_payment_relations
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
            f'User {self.user.get_full_name()} was removed from event "{self.event}" by {admin_user} on {timezone.now()}'
        )

        # Notify responsible group if someone is unattended after deadline
        if (
            timezone.now() >= self.event.unattend_deadline
            and not self.user_id == admin_user.id
        ):
            subject = f"[{self.event}] {self.user.get_full_name()} har blitt avmeldt arrangementet av {admin_user}"

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
        return f"Reservasjoner for {self.attendance_event.event.title}"

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
        "Event",
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
