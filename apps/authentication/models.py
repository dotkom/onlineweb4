# -*- coding: utf-8 -*-

import datetime
import hashlib
import logging
import urllib
from functools import reduce

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from rest_framework.exceptions import NotAcceptable

from apps.authentication.constants import FieldOfStudyType, GroupType, RoleType
from apps.authentication.validators import validate_rfid
from apps.gallery.models import ResponsiveImage
from apps.payment import status as PaymentStatus
from apps.permissions.models import ObjectPermissionModel

logger = logging.getLogger(__name__)

GENDER_CHOICES = [("male", _("mann")), ("female", _("kvinne"))]

COMMITTEES = [
    ("hs", _("Hovedstyret")),
    ("appkom", _("Applikasjonskomiteen")),
    ("arrkom", _("Arrangementskomiteen")),
    ("bankom", _("Bank- og økonomikomiteen")),
    ("bedkom", _("Bedriftskomiteen")),
    ("dotkom", _("Drifts- og utviklingskomiteen")),
    ("ekskom", _("Ekskursjonskomiteen")),
    ("fagkom", _("Fag- og kurskomiteen")),
    ("jubkom", _("Jubileumskomiteen")),
    ("pangkom", _("Pensjonistkomiteen")),
    ("prokom", _("Profil-og aviskomiteen")),
    ("redaksjonen", _("Redaksjonen")),
    ("seniorkom", _("Seniorkomiteen")),
    ("trikom", _("Trivselskomiteen")),
    ("velkom", _("Velkomstkomiteen")),
]

POSITIONS = [
    ("medlem", _("Medlem")),
    ("leder", _("Leder")),
    ("nestleder", _("Nestleder")),
    ("redaktor", _("Redaktør")),
    ("okoans", _("Økonomiansvarlig")),
]


def get_length_of_field_of_study(field_of_study):
    """
    Returns length of a field of study
    """
    if field_of_study in [
        FieldOfStudyType.GUEST,
        FieldOfStudyType.OTHER_MEMBER,
        FieldOfStudyType.SOCIAL_MEMBER,
    ]:
        return 0
    # dont return a bachelor student as 4th or 5th grade
    elif field_of_study == FieldOfStudyType.BACHELOR:
        return 3
    elif field_of_study in FieldOfStudyType.ALL_MASTERS:
        return 2
    elif field_of_study == FieldOfStudyType.PHD:
        return 99
    elif field_of_study == FieldOfStudyType.INTERNATIONAL:
        return 1
    # If user's field of study is not matched by any of these tests, return -1
    else:
        return 0


def get_length_of_membership(field_of_study: str) -> int:
    if field_of_study == FieldOfStudyType.SOCIAL_MEMBER:
        return 1
    else:
        return get_length_of_field_of_study(field_of_study)


def get_start_of_field_of_study(field_of_study):
    """
    Returns start year of a field of study
    """
    if field_of_study in [
        FieldOfStudyType.GUEST,
        FieldOfStudyType.OTHER_MEMBER,
        FieldOfStudyType.SOCIAL_MEMBER,
    ]:
        return 0
    elif field_of_study == FieldOfStudyType.BACHELOR:
        return 0
    elif field_of_study in FieldOfStudyType.ALL_MASTERS:
        return 3
    elif field_of_study == FieldOfStudyType.PHD:
        return 5
    elif field_of_study == FieldOfStudyType.INTERNATIONAL:
        return 0
    # If user's field of study is not matched by any of these tests, return -1
    else:
        return -1


class OnlineUser(AbstractUser):
    IMAGE_FOLDER = "images/profiles"
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".gif", ".png"]
    backend = "django.contrib.auth.backends.ModelBackend"

    # Online related fields
    field_of_study = models.SmallIntegerField(
        _("studieretning"),
        choices=FieldOfStudyType.ALL_CHOICES,
        default=FieldOfStudyType.GUEST,
    )
    started_date = models.DateField(_("startet studie"), default=datetime.date.today)
    compiled = models.BooleanField(_("kompilert"), default=False)

    # Mail
    infomail = models.BooleanField(_("vil ha infomail"), default=False)
    jobmail = models.BooleanField(_("vil ha oppdragsmail"), default=False)
    online_mail = models.CharField(
        _("Online-epost"), max_length=50, blank=True, null=True
    )

    # Address
    phone_number = models.CharField(
        _("telefonnummer"), max_length=20, blank=True, null=True
    )
    address = models.CharField(_("adresse"), max_length=100, blank=True, null=True)
    zip_code = models.CharField(_("postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_("matallergier/preferanser"), blank=True, null=True)
    rfid = models.CharField(
        _("RFID"),
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_rfid],
    )
    nickname = models.CharField(_("nickname"), max_length=50, blank=True, null=True)
    website = models.URLField(_("hjemmeside"), blank=True, null=True)
    github = models.URLField(_("github"), blank=True, null=True)
    linkedin = models.URLField(_("linkedin"), blank=True, null=True)
    gender = models.CharField(
        _("kjønn"), max_length=10, choices=GENDER_CHOICES, default="male"
    )
    bio = models.TextField(_("bio"), max_length=2048, blank=True)
    # NTNU credentials
    ntnu_username = models.CharField(
        _("NTNU-brukernavn"), max_length=50, blank=True, null=True, unique=True
    )

    # TODO checkbox for forwarding of @online.ntnu.no mail

    @property
    def is_member(self):
        """
        Returns true if the User object is associated with Online.
        """
        if self.ntnu_username:
            if (
                AllowedUsername.objects.filter(username=self.ntnu_username.lower())
                .filter(expiration_date__gte=timezone.now())
                .count()
                > 0
            ):
                return True
        return False

    @property
    def is_committee(self):
        # New check for committee membership
        memberships = GroupMember.objects.filter(user=self)
        for membership in memberships:
            if membership.group.group_type == GroupType.COMMITTEE:
                return True

        # Old check for committee membership for backwards compatibility
        try:
            committee_group = Group.objects.get(name="Komiteer")
            return self in committee_group.user_set.all() or self.is_staff
        except Group.DoesNotExist:
            # This probably means that a developer does not have the Komiteer group set up, so let's fail silently
            return False

    @property
    def has_expiring_membership(self):
        if self.ntnu_username:
            expiration_threshold = timezone.now() + datetime.timedelta(days=60)
            if (
                AllowedUsername.objects.filter(
                    username=self.ntnu_username.lower(),
                    expiration_date__lt=expiration_threshold,
                ).count()
                > 0
            ):
                return True
        return False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def primary_email(self) -> str:
        email_object = self.email_object
        if email_object:
            return email_object.email
        return None

    @property
    def email_object(self) -> "Email":
        return self.get_emails().filter(primary=True).first()

    def get_emails(self):
        return Email.objects.filter(user=self)

    def get_online_mail(self):
        if self.online_mail:
            return self.online_mail + "@" + settings.OW4_GSUITE_SYNC.get("DOMAIN")
        return None

    def get_active_suspensions(self):
        return self.suspension_set.filter(active=True)

    def in_group(self, group_name):
        return reduce(lambda x, y: x or y.name == group_name, self.groups.all(), False)

    def member(self):
        if not self.is_member:
            return None
        return AllowedUsername.objects.get(username=self.ntnu_username.lower())

    @property
    def saldo(self):
        value = (
            self.paymenttransaction_set.filter(status=PaymentStatus.DONE)
            .aggregate(coins=models.Sum("amount"))
            .get("coins", 0)
        )
        return 0 if value is None else value

    @property
    def year(self):
        start_year = get_start_of_field_of_study(self.field_of_study)
        length_of_study = get_length_of_field_of_study(self.field_of_study)
        today = timezone.now().date()
        started = self.started_date

        # We say that a year is 360 days in case we are a bit slower to
        # add users one year.
        years_passed = ((today - started).days // 360) + 1

        return min(start_year + years_passed, start_year + length_of_study)

    def get_absolute_url(self):
        return reverse("profiles_view", kwargs={"username": self.username})

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        if self.ntnu_username == "":
            self.ntnu_username = None
        self.username = self.username.lower()
        super(OnlineUser, self).save(*args, **kwargs)

    def serializable_object(self):
        if self.privacy.expose_phone_number:
            phone = self.phone_number
        else:
            phone = "Ikke tilgjengelig"

        return {
            "id": self.id,
            "phone": strip_tags(phone),
            "username": strip_tags(self.username),
            "value": strip_tags(self.get_full_name()),  # typeahead
            "name": strip_tags(self.get_full_name()),
            "image": self.get_image_url(75),
        }

    def get_image_url(self, size=50):
        default = "%s%s_%s.png" % (
            settings.BASE_URL,
            settings.DEFAULT_PROFILE_PICTURE_PREFIX,
            self.gender,
        )

        gravatar_url = (
            "https://www.gravatar.com/avatar/"
            + hashlib.md5(self.email.encode("utf-8")).hexdigest()
            + "?"
        )
        gravatar_url += urllib.parse.urlencode({"d": default, "s": str(size)})
        return gravatar_url

    @property
    def image(self):
        return self.get_image_url(240)

    def get_visible_as_attending_events(self):
        """ Returns the default value of visible_as_attending_events set in privacy/personvern """
        if hasattr(self, "privacy"):
            return self.privacy.visible_as_attending_events
        return False

    @property
    def mark_rules_accepted(self):
        from apps.marks.models import MarkRuleSet

        return MarkRuleSet.has_user_accepted_mark_rules(user=self)

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = _("brukerprofil")
        verbose_name_plural = _("brukerprofiler")
        permissions = (("view_onlineuser", "View OnlineUser"),)
        default_permissions = ("add", "change", "delete")


class Email(models.Model):
    user = models.ForeignKey(
        OnlineUser, related_name="email_user", on_delete=models.CASCADE
    )
    email = models.EmailField(_("epostadresse"), unique=True)
    primary = models.BooleanField(_("primær"), default=False)
    verified = models.BooleanField(_("verifisert"), default=False, editable=False)

    def save(self, *args, **kwargs):
        primary_email = self.user.email_object
        if not primary_email:
            self.primary = True
        elif primary_email.email != self.email:
            self.primary = False
        self.email = self.email.lower()
        if self.primary:
            self.user.email = self.email
            self.user.save()
        super(Email, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("epostadresse")
        verbose_name_plural = _("epostadresser")
        permissions = (("view_email", "View Email"),)
        default_permissions = ("add", "change", "delete")


class RegisterToken(models.Model):
    user = models.ForeignKey(
        OnlineUser, related_name="register_user", on_delete=models.CASCADE
    )
    email = models.EmailField(_("epost"), max_length=254)
    token = models.CharField(_("token"), max_length=32, unique=True)
    created = models.DateTimeField(
        _("opprettet dato"), editable=False, auto_now_add=True
    )

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = timezone.now()
        return now < self.created + valid_period

    class Meta:
        permissions = (("view_registertoken", "View RegisterToken"),)
        default_permissions = ("add", "change", "delete")


class AllowedUsername(models.Model):
    """
    Holds usernames that are considered valid members of Online and the time they expire.
    """

    username = models.CharField(_("NTNU-brukernavn"), max_length=10, unique=True)
    registered = models.DateField(_("registrert"))
    note = models.CharField(_("notat"), max_length=100)
    description = models.TextField(_("beskrivelse"), blank=True, null=True)
    expiration_date = models.DateField(_("utløpsdato"))

    @property
    def is_active(self):
        return timezone.now().date() < self.expiration_date

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super(AllowedUsername, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("medlem")
        verbose_name_plural = _("medlemsregister")
        ordering = ("username",)
        permissions = (("view_allowedusername", "View AllowedUsername"),)
        default_permissions = ("add", "change", "delete")


class Position(models.Model):
    """
    Contains a users position in the organization year range
    """

    period_start = models.DateField(default=datetime.date.today)
    period_end = models.DateField(default=datetime.date.today)
    committee = models.CharField(
        _("komité"), max_length=20, choices=COMMITTEES, default="hs"
    )
    position = models.CharField(
        _("stilling"), max_length=20, choices=POSITIONS, default="medlem"
    )
    user = models.ForeignKey(
        OnlineUser, related_name="positions", blank=False, on_delete=models.CASCADE
    )

    @property
    def period(self):
        return f"{self.period_start.year}-{self.period_end.year}"

    @property
    def print_string(self):
        return f"{self.period}: {self.committee} ({self.position})"

    def __str__(self):
        return self.print_string

    class Meta:
        verbose_name = _("posisjon")
        verbose_name_plural = _("posisjoner")
        ordering = ("user", "period_start", "period_end")
        permissions = (("view_position", "View Position"),)
        default_permissions = ("add", "change", "delete")


class SpecialPosition(models.Model):
    """
    Special object to represent special positions that typically lasts for life.
    """

    position = models.CharField(_("Posisjon"), max_length=50, blank=False)
    since_year = models.IntegerField(_("Medlem siden"))
    user = models.ForeignKey(
        OnlineUser,
        related_name="special_positions",
        blank=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s, %s" % (self.user.get_full_name(), self.position)

    class Meta:
        verbose_name = _("spesialposisjon")
        verbose_name_plural = _("spesialposisjoner")
        ordering = ("user", "since_year")
        permissions = (("view_specialposition", "View SpecialPosition"),)
        default_permissions = ("add", "change", "delete")


def get_default_group_roles():
    roles = [RoleType.LEADER, RoleType.DEPUTY_LEADER]
    for role in roles:
        GroupRole.get_for_type(role)
    return GroupRole.objects.filter(role_type__in=roles)


class OnlineGroup(ObjectPermissionModel, models.Model):
    """
    A group relating a Django group to a group in Online
    """

    """ The Django group this Online group relates to """
    group = models.OneToOneField(
        Group,
        verbose_name="Djangogruppe",
        primary_key=True,
        related_name="online_group",
        on_delete=models.CASCADE,
    )

    """ The short name of a group, eg. HS or Dotkom """
    name_short = models.CharField(
        _("Forkortelse"), null=False, blank=False, max_length=48
    )
    """ The long/full name of a group, like Hovedstyret or Drifts- og utviklingskomiteen """
    name_long = models.CharField(
        _("Fullt navn"), null=False, blank=False, max_length=128
    )
    description_short = models.TextField(
        _("Beskrivelse (kortfattet)"), max_length=2048, blank=True
    )
    description_long = models.TextField(
        _("Beskrivelse (helhetlig)"), max_length=2048, blank=True
    )
    application_description = models.TextField(
        _("Opptaksbeskrivelse"),
        max_length=2048,
        blank=True,
        help_text="Beskriv gruppen for de som ønsker å søke under et opptak",
    )
    email = models.EmailField(_("E-post"), max_length=128, blank=True)
    image = models.ForeignKey(
        ResponsiveImage,
        related_name="online_groups",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(_("Oprettelsesdato"), default=timezone.now)
    group_type = models.CharField(
        verbose_name=_("Gruppetype"),
        choices=GroupType.ALL_CHOICES,
        default=GroupType.COMMITTEE,
        max_length=256,
        null=False,
        blank=False,
    )
    parent_group = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        related_name="sub_groups",
        verbose_name=_("Administrerende gruppe"),
        blank=True,
        null=True,
    )
    roles = models.ManyToManyField(
        to="GroupRole",
        related_name="groups",
        verbose_name=_("Tilgjengelige roller"),
        default=get_default_group_roles,
    )
    admin_roles = models.ManyToManyField(
        to="GroupRole",
        related_name="admin_for_groups",
        verbose_name=_("Administrerende roller"),
        help_text=_("Roller som kan administrere denne gruppen og undergrupper"),
        default=get_default_group_roles,
    )

    @property
    def id(self):
        """ Proxy primary key/id from group object """
        return self.group.id

    def get_members_with_role(self, role: str):
        # Get role first instead of querying directly because the role may not exist yet
        role = GroupRole.get_for_type(role)
        return self.members.filter(roles=role)

    def get_users_with_role(self, role: str):
        return OnlineUser.objects.filter(
            group_memberships__in=self.get_members_with_role(role)
        )

    def add_user(self, user: OnlineUser):
        return GroupMember.objects.create(group=self, user=user)

    def remove_user(self, user: OnlineUser):
        self.members.filter(user=user).delete()

    @property
    def verbose_type(self):
        return self.get_group_type_display()

    def __str__(self):
        return self.name_short

    def _get_admin_members_query(self):
        """ Gather a single query for getting permitted member users from this group and parent groups. """
        query = models.Q(group=self, roles__in=self.admin_roles.all())
        if self.parent_group:
            query |= self.parent_group._get_admin_members_query()
        return query

    def get_permission_users(self):
        query = self._get_admin_members_query()
        members = GroupMember.objects.filter(query)
        users = OnlineUser.objects.filter(group_memberships__in=members)
        return users

    class Meta:
        verbose_name = _("Onlinegruppe")
        verbose_name_plural = _("Onlinegrupper")
        ordering = ("name_long",)
        permissions = (("view_onlinegroups", "View OnlineGroup"),)
        default_permissions = ("add", "change", "delete")


class GroupMember(ObjectPermissionModel, models.Model):
    """
    Model relating a user to an Online group
    """

    user = models.ForeignKey(
        OnlineUser,
        verbose_name="Bruker",
        related_name="group_memberships",
        on_delete=models.CASCADE,
        null=False,
    )
    group = models.ForeignKey(
        OnlineGroup,
        verbose_name="Onlinegruppe",
        related_name="members",
        on_delete=models.CASCADE,
        null=False,
    )
    added = models.DateTimeField(default=timezone.now)

    is_on_leave = models.BooleanField(_("Permittert"), default=False)
    is_retired = models.BooleanField(_("Pensjonert"), default=False)

    @property
    def is_active(self):
        return not (self.is_on_leave or self.is_retired)

    def has_role(self, role: RoleType):
        return self.roles.filter(role_type=role).exists()

    def get_permission_users(self):
        return self.group.get_permission_users()

    def __str__(self):
        return f"{self.user} - {self.group}"

    class Meta:
        verbose_name = _("Gruppemedlemskap")
        verbose_name_plural = _("Gruppemedlemskap")
        """ Users can only have 1 membership to each group """
        unique_together = (("user", "group"),)
        ordering = ("group", "user", "added")
        permissions = (("view_groupmember", "View GroupMember"),)
        default_permissions = ("add", "change", "delete")


class GroupRole(models.Model):
    memberships = models.ManyToManyField(
        GroupMember, verbose_name="Medlemskap", related_name="roles"
    )
    role_type = models.CharField(
        verbose_name="Rolle",
        choices=RoleType.ALL_CHOICES,
        max_length=256,
        null=False,
        blank=False,
        unique=True,
    )

    @classmethod
    def get_for_type(cls, role_type: str):
        if role_type not in RoleType.ALL_TYPES:
            raise ValueError(f"'{role_type}' is not a legal role_type")
        role, created = cls.objects.get_or_create(role_type=role_type)
        return role

    @property
    def verbose_name(self):
        return self.get_role_type_display()

    def __str__(self):
        return self.verbose_name

    class Meta:
        verbose_name = _("Medlemskapsrolle")
        verbose_name_plural = _("Medlemskapsroller")
        ordering = ("role_type",)
        permissions = (("view_grouprole", "View GroupRole"),)
        default_permissions = ("add", "change", "delete")
