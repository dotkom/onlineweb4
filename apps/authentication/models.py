# -*- coding: utf-8 -*-

import datetime
import hashlib
import urllib
from functools import reduce

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

# If this list is changed, remember to check that the year property on
# OnlineUser is still correct!
from apps.authentication.validators import validate_rfid

FIELD_OF_STUDY_CHOICES = [
    (0, _('Gjest')),
    (1, _('Bachelor i Informatikk')),
    # master degrees take up the interval [10,30]
    (10, _('Programvaresystemer')),
    (11, _('Databaser og søk')),
    (12, _('Algoritmer og datamaskiner')),
    (13, _('Spillteknologi')),
    (14, _('Kunstig intelligens')),
    (15, _('Helseinformatikk')),
    (16, _('Interaksjonsdesign, spill- og læringsteknologi')),
    (30, _('Annen mastergrad')),
    (40, _('Sosialt medlem')),
    (80, _('PhD')),
    (90, _('International')),
    (100, _('Annet Onlinemedlem')),
]

GENDER_CHOICES = [
    ("male", _("mann")),
    ("female", _("kvinne")),
]

COMMITTEES = [
    ('hs', _('Hovedstyret')),
    ('appkom', _('Applikasjonskomiteen')),
    ('arrkom', _('Arrangementskomiteen')),
    ('bankom', _('Bank- og økonomikomiteen')),
    ('bedkom', _('Bedriftskomiteen')),
    ('dotkom', _('Drifts- og utviklingskomiteen')),
    ('ekskom', _('Ekskursjonskomiteen')),
    ('fagkom', _('Fag- og kurskomiteen')),
    ('jubkom', _('Jubileumskomiteen')),
    ('pangkom', _('Pensjonistkomiteen')),
    ('prokom', _('Profil-og aviskomiteen')),
    ('redaksjonen', _('Redaksjonen')),
    ('seniorkom', _('Seniorkomiteen')),
    ('trikom', _('Trivselskomiteen')),
    ('velkom', _('Velkomstkomiteen')),
]

POSITIONS = [
    ('medlem', _('Medlem')),
    ('leder', _('Leder')),
    ('nestleder', _('Nestleder')),
    ('redaktor', _('Redaktør')),
    ('okoans', _('Økonomiansvarlig')),
]


def get_length_of_field_of_study(field_of_study):
    """
    Returns length of a field of study
    """
    if field_of_study == 0 or field_of_study == 100 or field_of_study == 40:  # others or social
        return 0
    # dont return a bachelor student as 4th or 5th grade
    elif field_of_study == 1:  # bachelor
        return 3
    elif 10 <= field_of_study <= 30:  # 10-30 is considered master
        return 2
    elif field_of_study == 80:  # phd
        return 99
    elif field_of_study == 90:  # international
        return 1
    # If user's field of study is not matched by any of these tests, return -1
    else:
        return 0


def get_start_of_field_of_study(field_of_study):
    """
    Returns start year of a field of study
    """
    if field_of_study == 0 or field_of_study == 100:  # others
        return 0
    elif field_of_study == 1:  # bachelor
        return 0
    elif 10 <= field_of_study <= 30:  # 10-30 is considered master
        return 3
    elif field_of_study == 40:  # social
        return 0
    elif field_of_study == 80:  # phd
        return 5
    elif field_of_study == 90:  # international
        return 0
    # If user's field of study is not matched by any of these tests, return -1
    else:
        return -1


class OnlineUser(AbstractUser):
    IMAGE_FOLDER = "images/profiles"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png']
    backend = 'django.contrib.auth.backends.ModelBackend'

    # Online related fields
    field_of_study = models.SmallIntegerField(_("studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_("startet studie"), default=datetime.date.today)
    compiled = models.BooleanField(_("kompilert"), default=False)

    # Mail
    infomail = models.BooleanField(_("vil ha infomail"), default=False)
    jobmail = models.BooleanField(_("vil ha oppdragsmail"), default=False)
    online_mail = models.CharField(_("Online-epost"), max_length=50, blank=True, null=True)

    # Address
    phone_number = models.CharField(_("telefonnummer"), max_length=20, blank=True, null=True)
    address = models.CharField(_("adresse"), max_length=100, blank=True, null=True)
    zip_code = models.CharField(_("postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_("allergier"), blank=True, null=True)
    mark_rules = models.BooleanField(_("godtatt prikkeregler"), default=False)
    rfid = models.CharField(_("RFID"), max_length=50, unique=True, blank=True, null=True, validators=[validate_rfid])
    nickname = models.CharField(_("nickname"), max_length=50, blank=True, null=True)
    website = models.URLField(_("hjemmeside"), blank=True, null=True)
    github = models.URLField(_("github"), blank=True, null=True)
    linkedin = models.URLField(_("linkedin"), blank=True, null=True)
    gender = models.CharField(_("kjønn"), max_length=10, choices=GENDER_CHOICES, default="male")
    bio = models.TextField(_("bio"), max_length=2048, blank=True)
    saldo = models.PositiveSmallIntegerField(_("saldo"), default=0, null=True)

    # NTNU credentials
    ntnu_username = models.CharField(_("NTNU-brukernavn"), max_length=50, blank=True, null=True, unique=True)

    # TODO checkbox for forwarding of @online.ntnu.no mail

    @property
    def is_member(self):
        """
        Returns true if the User object is associated with Online.
        """
        if self.ntnu_username:
            if AllowedUsername.objects.filter(
                username=self.ntnu_username.lower()
            ).filter(
                expiration_date__gte=timezone.now()
            ).count() > 0:
                return True
        return False

    @property
    def is_committee(self):
        try:
            committee_group = Group.objects.get(name='Komiteer')
            return self in committee_group.user_set.all() or self.is_staff
        except Group.DoesNotExist:
            # This probably means that a developer does not have the Komiteer group set up, so let's fail silently
            return False

    @property
    def has_expiring_membership(self):
        if self.ntnu_username:
            expiration_threshold = timezone.now() + datetime.timedelta(days=60)
            if AllowedUsername.objects.filter(
                    username=self.ntnu_username.lower(),
                    expiration_date__lt=expiration_threshold
            ).count() > 0:
                return True
        return False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_email(self):
        email = self.get_emails().filter(primary=True)
        if email:
            return email[0]
        return None

    def get_emails(self):
        return Email.objects.all().filter(user=self)

    def get_online_mail(self):
        if self.online_mail:
            return self.online_mail + '@' + settings.OW4_GSUITE_SYNC.get('DOMAIN')
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
    def year(self):
        start_year = get_start_of_field_of_study(self.field_of_study)
        length_of_study = get_length_of_field_of_study(self.field_of_study)
        today = timezone.now().date()
        started = self.started_date

        # We say that a year is 360 days in case we are a bit slower to
        # add users one year.
        years_passed = ((today - started).days // 360) + 1

        return min(start_year + years_passed, start_year + length_of_study)

    @models.permalink
    def get_absolute_url(self):
        return 'profiles_view', None, {'username': self.username}

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
            'id': self.id,
            'phone': strip_tags(phone),
            'username': strip_tags(self.username),
            'value': strip_tags(self.get_full_name()),  # typeahead
            'name': strip_tags(self.get_full_name()),
            'image': self.get_image_url(75),
        }

    def get_image_url(self, size=50):
        default = "%s%s_%s.png" % (settings.BASE_URL,
                                   settings.DEFAULT_PROFILE_PICTURE_PREFIX, self.gender)

        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.encode('utf-8')).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    def get_visible_as_attending_events(self):
        """ Returns the default value of visible_as_attending_events set in privacy/personvern """
        if hasattr(self, 'privacy'):
            return self.privacy.visible_as_attending_events
        return False

    class Meta(object):
        ordering = ['first_name', 'last_name']
        verbose_name = _("brukerprofil")
        verbose_name_plural = _("brukerprofiler")
        permissions = (
            ('view_onlineuser', 'View OnlineUser'),
        )


class Email(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="email_user")
    email = models.EmailField(_("epostadresse"), unique=True)
    primary = models.BooleanField(_("primær"), default=False)
    verified = models.BooleanField(_("verifisert"), default=False, editable=False)

    def save(self, *args, **kwargs):
        primary_email = self.user.get_email()
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

    class Meta(object):
        verbose_name = _("epostadresse")
        verbose_name_plural = _("epostadresser")
        permissions = (
            ('view_email', 'View Email'),
        )


class RegisterToken(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="register_user")
    email = models.EmailField(_("epost"), max_length=254)
    token = models.CharField(_("token"), max_length=32, unique=True)
    created = models.DateTimeField(_("opprettet dato"), editable=False, auto_now_add=True)

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = timezone.now()
        return now < self.created + valid_period

    class Meta(object):
        permissions = (
            ('view_registertoken', 'View RegisterToken'),
        )


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
        permissions = (
            ('view_allowedusername', 'View AllowedUsername'),
        )


class Position(models.Model):
    """
    Contains a users position in the organization from a given year
    """
    period = models.CharField(_('periode'), max_length=9, default="2013-2014", blank=False)
    committee = models.CharField(_("komite"), max_length=20, choices=COMMITTEES, default="hs")
    position = models.CharField(_("stilling"), max_length=20, choices=POSITIONS, default="medlem")
    user = models.ForeignKey(OnlineUser, related_name='positions', blank=False)

    @property
    def print_string(self):
        return '%s: %s(%s)' % (self.period, self.committee, self.position)

    def __str__(self):
        return self.print_string

    class Meta(object):
        verbose_name = _('posisjon')
        verbose_name_plural = _('posisjoner')
        ordering = ('user', 'period', )
        permissions = (
            ('view_position', 'View Position'),
        )


class SpecialPosition(models.Model):
    """
    Special object to represent special positions that typically lasts for life.
    """
    position = models.CharField(_('Posisjon'), max_length=50, blank=False)
    since_year = models.IntegerField(_('Medlem siden'))
    user = models.ForeignKey(OnlineUser, related_name='special_positions', blank=False)

    def __str__(self):
        return '%s, %s' % (self.user.get_full_name(), self.position)

    class Meta(object):
        verbose_name = _('spesialposisjon')
        verbose_name_plural = _('spesialposisjoner')
        ordering = ('user', 'since_year',)
        permissions = (
            ('view_specialposition', 'View SpecialPosition'),
        )
