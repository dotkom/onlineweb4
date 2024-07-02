from datetime import date, datetime, timedelta
from typing import NamedTuple

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

User = settings.AUTH_USER_MODEL

DURATION = 14
SUMMER = {"start": {"month": 6, "day": 1}, "end": {"month": 8, "day": 15}}
WINTER = {"start": {"month": 12, "day": 5}, "end": {"month": 1, "day": 10}}


class DateRange(NamedTuple):
    start: date
    end: date


def freeze_periods(year: int) -> list[DateRange]:
    summer = DateRange(date(year, **SUMMER["start"]), date(year, **SUMMER["end"]))
    winter = DateRange(date(year, **WINTER["start"]), date(year + 1, **WINTER["end"]))
    past_winter = DateRange(
        date(year - 1, **WINTER["start"]), date(year, **WINTER["end"])
    )
    return [past_winter, summer, winter]


def offset_for_freeze_periods(
    expiry: date, given: date, freeze: DateRange
) -> timedelta | None:
    start, end = freeze
    if start <= given <= end:
        return timedelta(days=(end - given).days)
    elif start < expiry < end:
        return timedelta(days=(end - start).days)
    return None


def delay_expiry_for_freeze_periods(given_date: date, expiry_date: date | datetime):
    for freeze in freeze_periods(expiry_date.year):
        offset = offset_for_freeze_periods(expiry_date, given_date, freeze)
        if offset is not None:
            # we assume they are not overlapping
            return expiry_date + offset
    return expiry_date


def user_weight(user: User, now: date | None = None) -> int:
    if now is None:
        now = timezone.now()

    curr_weight = Mark.marks.active(user, now=now).aggregate(
        total_weight=models.Sum("mark__weight")
    )
    return curr_weight["total_weight"] or 0


def signup_delay(user: User, event_signup: date) -> timedelta | None:
    match user_weight(user, event_signup):
        case 0:
            return None
        case 1:
            return timedelta(hours=1)
        case 2:
            return timedelta(hours=4)
        case _:
            # TODO: should we care about the suspension here?
            return timedelta(days=1)


class MarksManager(models.Manager):
    @staticmethod
    def all_active():
        return Mark.objects.filter(given_to__expiration_date__gt=timezone.now().date())

    @staticmethod
    def active(user, now: date | None = None):
        if not now:
            now = timezone.now().date()
        return MarkUser.objects.filter(user=user, expiration_date__gt=now)

    @staticmethod
    def inactive(user=None):
        return MarkUser.objects.filter(user=user).filter(
            expiration_date__lte=timezone.now().date()
        )


class Mark(models.Model):
    class Category(models.IntegerChoices):
        Ingen = 0, _("Ingen")
        Social = 1, _("Sosialt")
        CompanyPresentation = 2, _("Bedriftspresentasjon")
        Course = 3, _("Kurs")
        Feedback = 4, _("Tilbakemelding")
        Office = 5, _("Kontoret")
        Payment = 6, _("Betaling")

    class Cause(models.TextChoices):
        LATE_DEREGISTRATION = "sen avmelding", _("Avmelding etter avmeldingsfrist")
        VERY_LATE_DEREGISTRATION = (
            "veldig sen avmelding",
            _("Avmelding under 2 timer før arrangementstart"),
        )
        LATE_ARRIVAL = (
            "sent oppmøte",
            _("Oppmøte etter arrangementets start eller innslipp er ferdig"),
        )
        NO_ATTENDANCE = "manglende oppmøte", _("Manglende oppmøte")
        MISSED_FEEDBACK = (
            "manglende tilbakemelding",
            _("Svarte ikke på tilbakemeldingsskjema"),
        )
        MISSED_PAYMENT = "manglende betaling", _("Manglende betaling")
        OTHER = "annet", _("Ukjent grunn")

        def weight(self) -> int:
            match self:
                case self.LATE_DEREGISTRATION:
                    return 2
                case self.VERY_LATE_DEREGISTRATION:
                    return 3
                case self.NO_ATTENDANCE:
                    return 3
                case self.LATE_ARRIVAL:
                    return 3
                case self.MISSED_FEEDBACK:
                    return 1
                case self.MISSED_PAYMENT:
                    return 1
                case self.OTHER:
                    # marks used to last 24h by default
                    return 3

    title = models.CharField(_("tittel"), max_length=155)
    weight = models.SmallIntegerField(_("Vekting, se prikkreglene for veiledning"))
    added_date = models.DateField(_("utdelt dato"), default=datetime.now)
    given_by = models.ForeignKey(
        User,
        related_name="mark_given_by",
        verbose_name=_("gitt av"),
        editable=False,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    last_changed_date = models.DateTimeField(
        _("sist redigert"), auto_now=True, editable=False
    )
    last_changed_by = models.ForeignKey(
        User,
        related_name="marks_last_changed_by",
        verbose_name=_("sist redigert av"),
        editable=False,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )
    description = models.CharField(
        _("beskrivelse"),
        max_length=255,
        help_text=_(
            "Hvis dette feltet etterlates blankt vil det fylles med en standard grunn for typen prikk som er valgt."
        ),
        blank=True,
    )
    category = models.SmallIntegerField(
        _("kategori"), choices=Category.choices, default=0
    )
    cause = models.CharField(
        _("årsak"), max_length=30, choices=Cause.choices, default=Cause.OTHER
    )
    users = models.ManyToManyField(through="MarkUser", to=User, related_name="marks")

    # managers
    objects = models.Manager()  # default manager
    marks = MarksManager()  # active marks manager

    def save(self, *args, **kwargs) -> None:
        if self.weight is None:
            self.weight = self.Cause(self.cause).weight()

        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Prikk for %s") % self.title

    class Meta:
        verbose_name = _("Prikk")
        verbose_name_plural = _("Prikker")
        permissions = (("view_mark", "View Mark"),)
        default_permissions = ("add", "change", "delete")


class MarkUser(models.Model):
    """
    One entry for a user that has received a mark.
    """

    mark = models.ForeignKey(
        Mark, related_name="given_to", on_delete=models.CASCADE, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    expiration_date = models.DateField(_("utløpsdato"), editable=False)

    def save(self, *args, **kwargs) -> None:
        now = timezone.now()
        if (
            user_weight(self.user, now) >= 6
            and not self.user.suspensions.filter(
                active=True, cause=Suspension.Cause.MARKS
            ).exists()
        ):
            s = Suspension(
                title=_("For mange prikker på rad"),
                description=_(
                    "Du har fått en 14 dagers suspensjon grunnet du har fått 6 eller flere prikker på en gang."
                ),
                active=True,
                expiration_date=delay_expiry_for_freeze_periods(
                    given_date=now,
                    expiry_date=now + timedelta(days=14),
                ),
                user=self.user,
                cause=Suspension.Cause.MARKS,
            )
            s.save()

        if not self.expiration_date:
            self.expiration_date = delay_expiry_for_freeze_periods(
                now.date(), now.date() + timedelta(days=DURATION)
            )

        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Mark entry for user: %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")
        ordering = ("expiration_date",)
        permissions = (("view_userentry", "View UserEntry"),)
        default_permissions = ("add", "change", "delete")


def is_suspended(user: User, now: datetime | None = None):
    if now is None:
        now = timezone.now()

    for suspension in user.get_active_suspensions():
        if not suspension.expiration_date or suspension.expiration_date > now.date():
            return True

    return False


class Suspension(models.Model):
    class Cause(models.IntegerChoices):
        PAYMENT = 0, _("Manglende betaling")
        MARKS = 1, _("For mange prikker på rad")
        OTHER = 2, _("Annet, se beskrivelse")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suspensions")
    title = models.CharField(_("tittel"), max_length=64)
    description = models.CharField(_("beskrivelse"), max_length=255)
    active = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now=True, editable=False)
    # the mark is active up to but _not including_ the expiry date
    expiration_date = models.DateField(_("utløpsdato"), null=True, blank=True)

    # Using id because foreign key to Payment caused circular dependencies
    payment_id = models.IntegerField(null=True, blank=True)
    cause = models.SmallIntegerField(_("Årsak"), choices=Cause.choices)

    def __str__(self):
        return f"Suspension: {self.user}"

    class Meta:
        default_permissions = ("add", "change", "delete")

    # TODO URL


class MarkRuleSet(models.Model):
    """
    A version of the mark rules set by Linjeforeningen Online
    """

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    valid_from_date = models.DateTimeField(auto_now_add=True)
    """ Rules written in markdown """
    content = models.TextField(
        verbose_name="Regler", help_text="Regelsett skrevet i markdown"
    )
    version = models.CharField(max_length=128, verbose_name="Versjon", unique=True)

    @classmethod
    def get_current_rule_set(cls) -> "MarkRuleSet":
        """
        The latest set of mark rules which have become active
        """
        return (
            cls.objects.order_by("-valid_from_date")
            .exclude(valid_from_date__gt=timezone.now())
            .first()
        )  # type: ignore

    @classmethod
    def has_user_accepted_mark_rules(cls, user: User) -> bool:
        current_rules = cls.get_current_rule_set()
        return RuleAcceptance.objects.filter(user=user, rule_set=current_rules).exists()

    @classmethod
    def accept_mark_rules(cls, user: User):
        current_rules = cls.get_current_rule_set()
        if not cls.has_user_accepted_mark_rules(user):
            RuleAcceptance.objects.create(user=user, rule_set=current_rules)

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = "Prikkegelsett"
        verbose_name_plural = "Prikkeregelsett"
        ordering = ("-valid_from_date",)


class RuleAcceptance(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name="accepted_mark_rule_sets",
        verbose_name="Godkjente prikkeregelsett",
        on_delete=models.CASCADE,
        editable=False,
    )
    rule_set = models.ForeignKey(
        to=MarkRuleSet,
        related_name="user_accepts",
        verbose_name="Brukere som har akseptert",
        on_delete=models.CASCADE,
        editable=False,
    )
    accepted_date = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.rule_set} - {self.user}"

    class Meta:
        verbose_name = "Regelgodkjenning"
        verbose_name_plural = "Regelgodkjennelser"
        unique_together = (("user", "rule_set"),)
        ordering = ("rule_set", "accepted_date")
