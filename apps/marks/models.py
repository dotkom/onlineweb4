from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import InvalidOperation
from typing import NamedTuple, Self

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q, QuerySet, Sum
from django.utils import timezone
from django.utils.translation import gettext as _

User = settings.AUTH_USER_MODEL

DURATION = 14
SUMMER = {"start": {"month": 6, "day": 1}, "end": {"month": 8, "day": 15}}
WINTER = {"start": {"month": 12, "day": 5}, "end": {"month": 1, "day": 10}}


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
    duration = models.DurationField(
        _("Varighet på prikker"), default=timedelta(days=20)
    )
    acceptors = models.ManyToManyField(to=User, through="RuleAcceptance")

    @classmethod
    def get_current_rule_set(cls) -> Self:
        """
        The latest set of mark rules which have become active
        """
        current = (
            cls.objects.order_by("-valid_from_date")
            .exclude(valid_from_date__gt=timezone.now())
            .first()
        )
        if current is None:
            # this only happens in a new installation of OW4
            current = cls.objects.create(content="Testregler ikke bruk", version="TEST")
        return current

    @classmethod
    def get_current_rule_set_pk(cls):
        current = cls.get_current_rule_set()
        return current.pk

    @classmethod
    def has_user_accepted_mark_rules(cls, user: User) -> bool:
        current_rules = cls.get_current_rule_set()
        return current_rules.acceptors.filter(pk=user.pk).exists()

    @classmethod
    def accept_mark_rules(cls, user: User):
        current_rules = cls.get_current_rule_set()
        if not cls.has_user_accepted_mark_rules(user):
            current_rules.acceptors.add(user)

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = "Prikkegelsett"
        verbose_name_plural = "Prikkeregelsett"
        ordering = ("-valid_from_date",)


class MarksManager(models.Manager):
    @staticmethod
    def all_active():
        return Mark.objects.filter(expiration_date__gt=timezone.now().date())

    @staticmethod
    def active(user, now: date | None = None):
        if not now:
            now = timezone.now().date()
        return Mark.objects.filter(users__pk=user.pk, expiration_date__gt=now)

    @staticmethod
    def inactive(user=None):
        return Mark.objects.filter(
            users__pk=user.pk, expiration_date__lte=timezone.now().date()
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
        OTHER = "annet", _("Annet")

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
    weight = models.PositiveSmallIntegerField(
        _("Vekting"),
        help_text="Settes automatisk basert på årsak. Se prikkreglene for veiledning",
        blank=True,
    )
    added_date = models.DateField(_("utdelt dato"), default=date.today)
    given_by = models.ForeignKey(
        User,
        related_name="mark_given_by",
        verbose_name=_("gitt av"),
        editable=False,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
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
        on_delete=models.SET_NULL,
    )
    description = models.TextField(
        _("beskrivelse"),
        max_length=255,
        help_text=_("Settes automatisk basert på årsak."),
        blank=True,
    )
    category = models.SmallIntegerField(
        _("kategori"), choices=Category.choices, default=0, editable=False
    )
    cause = models.CharField(
        _("årsak"), max_length=30, choices=Cause.choices, default=Cause.OTHER
    )
    users = models.ManyToManyField(through="MarkUser", to=User, related_name="marks")
    ruleset = models.ForeignKey(
        verbose_name=_("Gjeldene prikkregler"),
        to="MarkRuleSet",
        default=MarkRuleSet.get_current_rule_set_pk,
        on_delete=models.CASCADE,
        editable=False,
    )
    expiration_date = models.DateField(_("Utløpsdato"))

    # managers
    objects = models.Manager()  # default manager
    marks = MarksManager()  # active marks manager

    def save(self, *args, **kwargs):
        self.expiration_date = delay_expiry_for_freeze_periods(
            self.added_date, self.added_date + self.ruleset.duration
        )

        if not self.pk:
            self.weight = self.Cause(self.cause).weight()

        if not self.description:
            self.description = self.Cause(self.cause).label

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    """this is here for historical reasons, the mark system used to have expirations build on each other"""
    expiration_date = models.DateField(
        _("utløpsdato"), editable=False, null=True, blank=True, default=None
    )

    def __str__(self):
        return _("Prikk gitt til: %s") % self.user.get_full_name()

    def save(self, *args, **kwargs):
        now = timezone.now()

        if (
            user_weight(self.user) + self.mark.weight >= 6
            and not Suspension.active_suspensions(self.user)
            .filter(cause=Suspension.Cause.MARKS)
            .exists()
        ):
            s = Suspension(
                title=_("For mange prikker på rad"),
                description=_(
                    "Du har fått en 14 dagers suspensjon grunnet du har fått 6 eller flere prikker på en gang."
                ),
                expiration_date=delay_expiry_for_freeze_periods(
                    given_date=now.date(),
                    expiry_date=now.date() + timedelta(days=14),
                ),
                user=self.user,
                cause=Suspension.Cause.MARKS,
            )
            s.save()

        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("user", "mark")
        ordering = ("expiration_date",)
        permissions = (("view_userentry", "View UserEntry"),)
        default_permissions = ("add", "change", "delete")


class Suspension(models.Model):
    class Cause(models.IntegerChoices):
        PAYMENT = 0, _("Manglende betaling")
        MARKS = 1, _("For mange prikker på rad")
        OTHER = 2, _("Annet, se beskrivelse")

    @classmethod
    def active_suspensions(
        cls, user: User, today: date | None = None
    ) -> QuerySet[Self]:
        """
        Currently active suspensions affecting an user.
        """
        if today is None:
            today = date.today()

        return cls.objects.filter(
            Q(user=user)
            & (Q(expiration_date__isnull=True) | Q(expiration_date__gt=today))
        )

    @classmethod
    def inactive_suspensions(
        cls, user: User, today: date | None = None
    ) -> QuerySet[Self]:
        """
        Suspensions no longer affecting an user
        """
        if today is None:
            today = date.today()

        return cls.objects.filter(user=user, expiration_date__lte=today)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    title = models.CharField(_("tittel"), max_length=64)
    description = models.CharField(_("beskrivelse"), max_length=255)
    created_time = models.DateTimeField(
        default=timezone.now, editable=False, verbose_name=_("Utdelt tidspunkt")
    )
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


class DateRange(NamedTuple):
    start: date
    end: date


@dataclass
class MarkDelay:
    delay: timedelta


@dataclass
class Suspended:
    pass


type UserSanction = MarkDelay | Suspended


def sanction_users(
    sanction: Mark | Suspension,
    users: list[User] | None = None,
    now: datetime | None = None,
):
    if now is None:
        now = timezone.now()

    def sanction_mark(mark: Mark, users: list[User], now: datetime):
        def should_be_suspended(u: User, today: date):
            return (
                user_weight(u, today) + mark.weight >= 6
                and not Suspension.active_suspensions(u, today)
                .filter(cause=Suspension.Cause.MARKS)
                .exists()
            )

        mark.users.set(users)

        suspensions = [
            Suspension(
                title=_("For mange prikker på rad"),
                description=_(
                    "Du har fått en 14 dagers suspensjon grunnet du har fått 6 eller flere prikker på en gang."
                ),
                expiration_date=delay_expiry_for_freeze_periods(
                    given_date=now.date(),
                    expiry_date=now.date() + timedelta(days=14),
                ),
                created_time=now,
                user=user,
                cause=Suspension.Cause.MARKS,
            )
            for user in users
            if should_be_suspended(user, now.date())
        ]

        Suspension.objects.bulk_create(suspensions)

    match sanction:
        case Mark():
            with transaction.atomic():
                sanction.save()
                assert users is not None
                sanction_mark(sanction, users, now)
        case Suspension():
            # it is strange that this does not support a list of users
            assert users is None
            sanction.save()
        case _:
            raise InvalidOperation("Invalid sanction")


def user_sanctions(user: User, today: date | None = None) -> UserSanction | None:
    if today is None:
        today = date.today()

    if Suspension.active_suspensions(user, today).exists():
        return Suspended()

    match user_weight(user, today):
        case 0:
            return None
        case 1:
            return MarkDelay(timedelta(hours=1))
        case 2:
            return MarkDelay(timedelta(hours=4))
        case w if 3 <= w < 6:
            return MarkDelay(timedelta(days=1))
        case _:
            return Suspended()


def freeze_periods(year: int) -> list[DateRange]:
    summer = DateRange(date(year, **SUMMER["start"]), date(year, **SUMMER["end"]))
    winter = DateRange(date(year, **WINTER["start"]), date(year + 1, **WINTER["end"]))
    past_winter = DateRange(
        date(year - 1, **WINTER["start"]), date(year, **WINTER["end"])
    )
    return [past_winter, summer, winter]


def offset_for_freeze_period(
    expiry: date, given: date, freeze: DateRange
) -> timedelta | None:
    start, end = freeze
    if start <= given <= end:
        return timedelta(days=(end - given).days)
    elif start < expiry < end:
        return timedelta(days=(end - start).days)
    return None


def delay_expiry_for_freeze_periods(given_date: date, expiry_date: date):
    for freeze in freeze_periods(expiry_date.year):
        offset = offset_for_freeze_period(expiry_date, given_date, freeze)
        if offset is not None:
            # we assume they are not overlapping
            return expiry_date + offset
    return expiry_date


def user_weight(user: User, today: date | None = None) -> int:
    if today is None:
        today = date.today()

    curr_weight = Mark.marks.active(user, now=today).aggregate(
        total_weight=Sum("weight")
    )
    return curr_weight["total_weight"] or 0
