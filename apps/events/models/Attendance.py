from datetime import datetime, timedelta
from random import choice as random_choice
from typing import List

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
from apps.marks.models import get_expiration_date
from apps.payment import status as payment_status
from apps.payment.mixins import PaymentMixin

from .Event import User, logger
from .Extras import Extras


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
        from apps.events.utils import (  # Imported here to avoid circular import
            handle_waitlist_bump,
        )

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

        response = {"status": False, "message": "", "status_code": None}

        # User is already an attendee
        if self.attendees.filter(user=user).exists():
            response["message"] = "Du er allerede meldt på dette arrangementet."
            response["status_code"] = 404
            return response

        # Registration closed
        if timezone.now() > self.registration_end:
            response["message"] = _("Påmeldingen er ikke lenger åpen.")
            response["status_code"] = 502
            return response

        # Room for me on the event?
        if not self.room_on_event:
            response["message"] = _("Det er ikke mer plass på dette arrangementet.")
            response["status_code"] = 503
            return response

        #
        # Offset calculations.
        #

        # Are there any rules preventing me from attending?
        # This should be checked last of the offsets, because it can completely deny you access.
        response = self.rules_satisfied(user)

        if not response["status"]:
            if "offset" not in response:
                return response

        # Do I have any marks that postpone my registration date?
        response = self._check_marks(response, user)

        # Return response if offset was set.
        if "offset" in response and response["offset"] > timezone.now():
            return response

        #
        # Offset calculations end
        #

        # Registration not open
        if timezone.now() < self.registration_start:
            response["status"] = False
            response["message"] = _("Påmeldingen har ikke åpnet enda.")
            response["status_code"] = 501
            return response

        # Is suspended
        if self.is_suspended(user):
            response["status"] = False
            response["message"] = _("Du er suspendert og kan ikke melde deg på.")
            response["status_code"] = 402

            return response

        # Checks if the event is group restricted and if the user is in the right group
        if not self.event.can_display(user):
            response["status"] = False
            response["message"] = _(
                "Du har ikke tilgang til å melde deg på dette arrangementet."
            )
            response["status_code"] = 403

            return response

        # No objections, set eligible.
        response["status"] = True
        return response

    def get_minimum_rule_offset_for_user(self, user: User):
        offsets_deltas = [
            rule_bundle.get_minimum_offset_for_user(user)
            for rule_bundle in self.rule_bundles.all()
        ]
        if len(offsets_deltas) == 0:
            return timezone.timedelta(hours=0)
        offsets_deltas.sort()
        return offsets_deltas[0]

    def _check_marks(self, response: dict, user: User):
        expiry_date = get_expiration_date(user)
        if expiry_date and expiry_date > timezone.now().date():
            # Offset is currently 1 day if you have marks, regardless of amount.
            mark_offset = timedelta(days=1)
            rule_offset = self.get_minimum_rule_offset_for_user(user)
            postponed_registration_start = (
                self.registration_start + rule_offset + mark_offset
            )

            before_expiry = self.registration_start.date() < expiry_date

            if postponed_registration_start > timezone.now() and before_expiry:
                if (
                    "offset" in response
                    and response["offset"] < postponed_registration_start
                    or "offset" not in response
                ):
                    response["status"] = False
                    response["status_code"] = 401
                    response["message"] = _("Din påmelding er utsatt grunnet prikker.")
                    response["offset"] = postponed_registration_start
        return response

    def _process_rulebundle_satisfaction_responses(self, responses):
        # Put the smallest offset faaar into the future.
        smallest_offset = timezone.now() + timedelta(days=365)
        offset_response = {}
        future_response = {}
        errors = []

        for response in responses:
            if response["status"]:
                return response
            elif "offset" in response:
                if response["offset"] < smallest_offset:
                    smallest_offset = response["offset"]
                    offset_response = response
            elif response["status_code"] == 402:
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
            return {"status": True, "status_code": 201}

        # If the user is not a member, return False right away
        # TODO check for guest list
        if not user.is_member:
            return {
                "status": False,
                "message": _("Dette arrangementet er kun åpent for medlemmer."),
                "status_code": 400,
            }

        # If there are no rule_bundles on this object, all members of Online are allowed.
        if not self.rule_bundles.exists() and user.is_member:
            return {"status": True, "status_code": 200}

        # Check all rule bundles
        responses = []

        # If one satisfies, return true, else append to the error list
        for rule_bundle in self.rule_bundles.all():
            responses.extend(rule_bundle.satisfied(user, self.registration_start))

        return self._process_rulebundle_satisfaction_responses(responses)

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

    def can_refund_payment(self, payment_relation) -> (bool, str):
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

    def get_payment_receipt_items(self, payment_relation) -> List[dict]:
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
        if (
            timezone.now() >= self.event.unattend_deadline
            and not self.user_id == admin_user.id
        ):
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
