# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models import Case, ExpressionWrapper, F, Q, When
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.approval import settings as approval_settings
from apps.authentication.constants import FieldOfStudyType
from apps.authentication.models import OnlineGroup

User = settings.AUTH_USER_MODEL


class Approval(models.Model):
    applicant = models.ForeignKey(
        User,
        verbose_name=_("søker"),
        related_name="applications",
        editable=True,
        on_delete=models.CASCADE,
    )
    approver = models.ForeignKey(
        User,
        verbose_name=_("godkjenner"),
        related_name="approved_applications",
        blank=True,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(_("opprettet"), auto_now_add=True)
    processed = models.BooleanField(_("behandlet"), default=False, editable=False)
    processed_date = models.DateTimeField(_("behandlet dato"), blank=True, null=True)
    approved = models.BooleanField(_("godkjent"), default=False, editable=False)
    message = models.TextField(_("melding"))

    class Meta:
        default_permissions = ("add", "change", "delete")


class MembershipApproval(Approval):
    new_expiry_date = models.DateField(_("ny utløpsdato"), blank=True, null=True)
    field_of_study = models.SmallIntegerField(
        _("studieretning"),
        choices=FieldOfStudyType.ALL_CHOICES,
        default=FieldOfStudyType.GUEST,
    )
    started_date = models.DateField(_("startet dato"), blank=True, null=True)
    documentation = models.ImageField(
        upload_to=approval_settings.DOCUMENTATION_PATH,
        blank=True,
        null=True,
        default=None,
    )

    def is_membership_application(self):
        if self.new_expiry_date:
            return True
        return False

    def is_fos_application(self):
        if self.field_of_study != 0 and self.started_date:
            return True
        return False

    def has_documentation(self):
        if self.documentation:
            return True
        return False

    def __str__(self):
        output = ""
        if self.is_fos_application():
            output = _("studieretningssøknad ")
        if self.is_membership_application():
            if not output:
                output = _("Medlemskapssøknad ")
            else:
                output = _("Medlemskaps- og ") + output
        if not output:
            return _("Tom søknad for %s") % self.applicant.get_full_name()
        return output + "for " + self.applicant.get_full_name()

    class Meta:
        verbose_name = _("medlemskapssøknad")
        verbose_name_plural = _("medlemskapssøknader")
        permissions = (("view_membershipapproval", "View membership approval"),)
        default_permissions = ("add", "change", "delete")


class CommitteeApplicationPeriodManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        return (
            super()
            .get_queryset()
            .annotate(
                actual_deadline=ExpressionWrapper(
                    F("deadline") + F("deadline_delta"),
                    output_field=models.DateTimeField(),
                )
            )
            .annotate(
                accepting_applications=Case(
                    When(Q(start__lte=now, actual_deadline__gte=now), then=True),
                    default=False,
                    output_field=models.BooleanField(),
                )
            )
        )

    def filter_overlapping(self, start: timezone.datetime, deadline: timezone.datetime):
        return (
            self.get_queryset()
            .filter(
                Q(start__range=[start, deadline])
                | Q(deadline__range=[start, deadline])
                | (
                    Q(start__lte=start, deadline__gte=start)
                    & Q(start__lte=deadline, deadline__gte=deadline)
                )
            )
            .distinct()
        )


class CommitteeApplicationPeriod(models.Model):
    objects = CommitteeApplicationPeriodManager()

    title = models.CharField(_("Tittel"), max_length=128)
    start = models.DateTimeField(_("Starttid"))
    deadline = models.DateTimeField(_("First"))
    # We have a deadline delta because we often accept applications after the actual deadline.
    deadline_delta = models.DurationField(
        _("Slingringsmonn"),
        help_text="Hvor lenge etter fristen skal det være mulig å søke?",
        default=timezone.timedelta(days=1),
    )
    committees = models.ManyToManyField(
        to=OnlineGroup, verbose_name=_("Komiteer"), related_name="application_periods"
    )

    def accepting_applications_at_time(self, time: timezone.datetime) -> bool:
        is_after_start = time >= self.start
        is_before_deadline = time <= self.actual_deadline
        return is_after_start and is_before_deadline

    @property
    def year(self) -> str:
        start_year = self.start.year
        end_year = self.deadline.year
        if start_year == end_year:
            return str(start_year)
        return f"{start_year} - {end_year}"

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        verbose_name = _("Opptaksperiode")
        verbose_name_plural = _("Opptaksperioder")
        ordering = ("-start", "-deadline")


class CommitteeApplication(models.Model):
    created = models.DateTimeField("opprettet", auto_now_add=True)
    modified = models.DateTimeField("endret", auto_now=True)

    applicant = models.ForeignKey(
        User,
        verbose_name="søker",
        blank=True,
        null=True,
        on_delete=models.deletion.CASCADE,
    )
    name = models.CharField("navn", max_length=69, blank=True, null=True)
    email = models.EmailField("e-postadresse", blank=True, null=True)

    application_text = models.TextField("søknadstekst")
    prioritized = models.BooleanField("prioriter komitevalg", default=False)
    committees = models.ManyToManyField(
        OnlineGroup, verbose_name="komiteer", through="CommitteePriority"
    )
    application_period = models.ForeignKey(
        to=CommitteeApplicationPeriod,
        verbose_name=_("Opptaksperiode"),
        related_name="applications",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    def get_name(self):
        return self.applicant if self.applicant else self.name

    get_name.short_description = "navn"

    def get_email(self):
        return self.applicant.primary_email if self.applicant else self.email

    def get_absolute_url(self):
        return reverse("admin:approval_committeeapplication_change", args=(self.pk,))

    def __str__(self):
        return "{created}: {applicant}".format(
            applicant=self.get_name(), created=self.created.strftime("%Y-%m-%d")
        )

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        verbose_name = "komitesøknad"
        verbose_name_plural = "komitesøknader"


class CommitteePriority(models.Model):
    valid_priorities = [(1, "1. prioritet"), (2, "2. prioritet"), (3, "3. prioritet")]

    committee_application = models.ForeignKey(
        CommitteeApplication, verbose_name="søknad", on_delete=models.deletion.CASCADE
    )
    group = models.ForeignKey(
        OnlineGroup, verbose_name="komite", on_delete=models.deletion.CASCADE
    )
    priority = models.SmallIntegerField("prioritet", choices=valid_priorities)

    def __str__(self):
        if self.committee_application.prioritized:
            return "{committee}: {priority}".format(
                committee=self.group, priority=self.get_priority_display()
            )
        return "{committee}".format(committee=self.group)

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        verbose_name = "komiteprioritering"
        verbose_name_plural = "komiteprioriteringer"
