# -*- coding: utf-8 -*-

import datetime
import urllib
import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.html import strip_tags

import watson
import reversion

# If this list is changed, remember to check that the year property on
# OnlineUser is still correct!
FIELD_OF_STUDY_CHOICES = [
    (0, _(u'Gjest')),
    (1, _(u'Bachelor i Informatikk (BIT)')),
    # master degrees take up the interval [10,30]
    (10, _(u'Programvaresystemer (P)')),
    (11, _(u'Databaser og søk (DS)')),
    (12, _(u'Algoritmer og datamaskiner (AD)')),
    (13, _(u'Spillteknologi (S)')),
    (14, _(u'Kunstig intelligens (KI)')),
    (15, _(u'Helseinformatikk (MSMEDTEK)')),
    (30, _(u'Annen mastergrad')),
    (80, _(u'PhD')),
    (90, _(u'International')),
    (100, _(u'Annet Onlinemedlem')),
]

GENDER_CHOICES = [
    ("male", _(u"mann")),
    ("female", _(u"kvinne")),
]

COMMITTEES = [
    ('hs', _(u'Hovedstyret')),
    ('appkom', _(u'Applikasjonskomiteen')),
    ('arrkom', _(u'Arrangementskomiteen')),
    ('bankom', _(u'Bank- og økonomikomiteen')),
    ('bedkom', _(u'Bedriftskomiteen')),
    ('dotkom', _(u'Drifts- og utviklingskomiteen')),
    ('ekskom', _(u'Ekskursjonskomiteen')),
    ('fagkom', _(u'Fag- og kurskomiteen')),
    ('jubkom', _(u'Jubileumskomiteen')),
    ('pangkom', _(u'Pensjonistkomiteen')),
    ('prokom', _(u'Profil-og aviskomiteen')),
    ('redaksjonen', _(u'Redaksjonen')),
    ('trikom', _(u'Trivselskomiteen')),
    ('velkom', _(u'Velkomstkomiteen')),
]

POSITIONS = [
    ('medlem', _(u'Medlem')),
    ('leder', _(u'Leder')),
    ('nestleder', _(u'Nestleder')),
    ('redaktor', _(u'Redaktør')),
    ('okoans', _(u'Økonomiansvarlig')),
]


def get_length_of_field_of_study(field_of_study):
    """
    Returns length of a field of study
    """
    if field_of_study == 0 or field_of_study == 100:  # others
        return 0
    # dont return a bachelor student as 4th or 5th grade
    elif field_of_study == 1:  # bachelor
        return 3
    elif 10 <= field_of_study <= 30:  # 10-30 is considered master
        return 2
    elif field_of_study == 80:  # phd
        return 3
    elif field_of_study == 90:  # international
        return 1
    # If user's field of study is not matched by any of these tests, return -1
    else:
        return 0


class OnlineUser(AbstractUser):

    IMAGE_FOLDER = "images/profiles"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png']

    # Online related fields
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_(u"startet studie"), default=datetime.date.today)
    compiled = models.BooleanField(_(u"kompilert"), default=False)

    # Mail
    infomail = models.BooleanField(_(u"vil ha infomail"), default=False)
    jobmail = models.BooleanField(_(u"vil ha oppdragsmail"), default=False)
    online_mail = models.CharField(_(u"Online-epost"), max_length=50, blank=True, null=True)

    # Address
    phone_number = models.CharField(_(u"telefonnummer"), max_length=20, blank=True, null=True)
    address = models.CharField(_(u"adresse"), max_length=100, blank=True, null=True)
    zip_code = models.CharField(_(u"postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_(u"allergier"), blank=True, null=True)
    mark_rules = models.BooleanField(_(u"godtatt prikkeregler"), default=False)
    rfid = models.CharField(_(u"RFID"), max_length=50, blank=True, null=True)
    nickname = models.CharField(_(u"nickname"), max_length=50, blank=True, null=True)
    website = models.URLField(_(u"hjemmeside"), blank=True, null=True)
    github = models.URLField(_(u"github"), blank=True, null=True)
    linkedin = models.URLField(_(u"linkedin"), blank=True, null=True)
    gender = models.CharField(_(u"kjønn"), max_length=10, choices=GENDER_CHOICES, default="male")
    bio = models.TextField(_(u"bio"), blank=True)

    # NTNU credentials
    ntnu_username = models.CharField(_(u"NTNU-brukernavn"), max_length=10, blank=True, null=True, unique=True)

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
            return self in committee_group.user_set.all() or self.is_staff()
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
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_email(self):
        email = self.get_emails().filter(primary=True)
        if email:
            return email[0]
        return None

    def get_emails(self):
        return Email.objects.all().filter(user=self)

    def in_group(self, group_name):
        return reduce(lambda x, y: x or y.name == group_name, self.groups.all(), False)

    def member(self):
        if not self.is_member:
            return None
        return AllowedUsername.objects.get(username=self.ntnu_username.lower())

    @property
    def year(self):
        today = timezone.now().date()
        started = self.started_date

        # We say that a year is 360 days incase we are a bit slower to
        # add users one year.
        year = ((today - started).days / 360) + 1

        if self.field_of_study == 0 or self.field_of_study == 100:  # others
            return 0
        # dont return a bachelor student as 4th or 5th grade
        elif self.field_of_study == 1:  # bachelor
            if year > 3:
                return 3
            return year
        elif 10 <= self.field_of_study <= 30:  # 10-30 is considered master
            if year >= 2:
                return 5
            return 4
        elif self.field_of_study == 80:  # phd
            return year + 5
        elif self.field_of_study == 90:  # international
            if year == 1:
                return 1
            return 4
        # If user's field of study is not matched by any of these tests, return -1
        else:
            return -1

    @models.permalink
    def get_absolute_url(self):
        return 'profiles_view', None, {'username': self.username}

    def __unicode__(self):
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

        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.email).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    class Meta(object):
        ordering = ['first_name', 'last_name']
        verbose_name = _(u"brukerprofil")
        verbose_name_plural = _(u"brukerprofiler")
        permissions = (
            ('view_onlineuser', 'View OnlineUser'),
        )


reversion.register(OnlineUser)


class Email(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="email_user")
    email = models.EmailField(_(u"epostadresse"), unique=True)
    primary = models.BooleanField(_(u"primær"), default=False)
    verified = models.BooleanField(_(u"verifisert"), default=False, editable=False)

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

    def __unicode__(self):
        return self.email

    class Meta(object):
        verbose_name = _(u"epostadresse")
        verbose_name_plural = _(u"epostadresser")
        permissions = (
            ('view_email', 'View Email'),
        )


reversion.register(Email)


class RegisterToken(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="register_user")
    email = models.EmailField(_(u"epost"), max_length=254)
    token = models.CharField(_(u"token"), max_length=32)
    created = models.DateTimeField(_(u"opprettet dato"), editable=False, auto_now_add=True)

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = timezone.now()
        return now < self.created + valid_period

    class Meta(object):
        permissions = (
            ('view_registertoken', 'View RegisterToken'),
        )


reversion.register(RegisterToken)


class AllowedUsername(models.Model):
    """
    Holds usernames that are considered valid members of Online and the time they expire.
    """
    username = models.CharField(_(u"NTNU-brukernavn"), max_length=10, unique=True)
    registered = models.DateField(_(u"registrert"))
    note = models.CharField(_(u"notat"), max_length=100)
    description = models.TextField(_(u"beskrivelse"), blank=True, null=True)
    expiration_date = models.DateField(_(u"utløpsdato"))

    @property
    def is_active(self):
        return timezone.now().date() < self.expiration_date

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super(AllowedUsername, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _(u"medlem")
        verbose_name_plural = _(u"medlemsregister")
        ordering = (u"username",)
        permissions = (
            ('view_allowedusername', 'View AllowedUsername'),
        )


reversion.register(AllowedUsername)


class Position(models.Model):
    """
    Contains a users position in the organization from a given year
    """
    period = models.CharField(_(u'periode'), max_length=9, default="2013-2014", blank=False)
    committee = models.CharField(_(u"komite"), max_length=20, choices=COMMITTEES, default="hs")
    position = models.CharField(_(u"stilling"), max_length=20, choices=POSITIONS, default="medlem")
    user = models.ForeignKey(OnlineUser, related_name='positions', blank=False)

    @property
    def print_string(self):
        return '%s: %s(%s)' % (self.period, self.committee, self.position)

    def __unicode__(self):
        return self.print_string

    class Meta(object):
        verbose_name = _(u'posisjon')
        verbose_name_plural = _(u'posisjoner')
        ordering = ('user', 'period', )
        permissions = (
            ('view_position', 'View Position'),
        )


reversion.register(Position)


class SpecialPosition(models.Model):
    """
    Special object to represent special positions that typically lasts for life.
    """
    position = models.CharField(_(u'Posisjon'), max_length=50, blank=False)
    since_year = models.IntegerField(_(u'Medlem siden'))
    user = models.ForeignKey(OnlineUser, related_name='special_positions', blank=False)

    def __unicode__(self):
        return '%s, %s' % (self.user.get_full_name(), self.position)

    class Meta(object):
        verbose_name = _(u'spesialposisjon')
        verbose_name_plural = _(u'spesialposisjoner')
        ordering = ('user', 'since_year',)
        permissions = (
            ('view_specialposition', 'View SpecialPosition'),
        )


reversion.register(SpecialPosition)


# Register OnlineUser in watson index for searching
watson.register(OnlineUser, fields=('first_name', 'last_name', 'ntnu_username', 'nickname'))
