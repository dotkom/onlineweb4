# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext as _


# If this list is changed, remember to check that the year property on
# OnlineUser is still correct!
FIELD_OF_STUDY_CHOICES = [
    (0, _(u'Gjest')),
    (1, _(u'Bachelor i Informatikk (BIT)')),
    # master degrees take up the interval [10,30>
    (10, _(u'Software (SW)')),
    (11, _(u'Informasjonsforvaltning (DIF)')),
    (12, _(u'Komplekse Datasystemer (KDS)')),
    (13, _(u'Spillteknologi (SPT)')),
    (14, _(u'Intelligente Systemer (IRS)')),
    (15, _(u'Helseinformatikk (MSMEDTEK)')),
    (30, _(u'Annen mastergrad')),
    (80, _(u'PhD')),
    (90, _(u'International')),
    (100, _(u'Annet Onlinemedlem')),
]

class OnlineUser(AbstractUser):

    IMAGE_FOLDER = "images/profiles"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png']
    
    # Online related fields
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_(u"startet studie"), default=datetime.datetime.now())
    compiled = models.BooleanField(_(u"kompilert"), default=False)

    # Email
    infomail = models.BooleanField(_(u"vil ha infomail"), default=True)

    # Address
    phone_number = models.CharField(_(u"telefonnummer"), max_length=20, blank=True, null=True)
    address = models.CharField(_(u"adresse"), max_length=30, blank=True, null=True)
    zip_code = models.CharField(_(u"postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_(u"allergier"), blank=True, null=True)
    mark_rules = models.BooleanField(_(u"godtatt prikkeregler"), default=False)
    rfid = models.CharField(_(u"RFID"), max_length=50, blank=True, null=True)
    nickname = models.CharField(_(u"nickname"), max_length=50, blank=True, null=True)
    website = models.CharField(_(u"hjemmeside"), max_length=50, blank=True, null=True)

    image = models.ImageField(_(u"bilde"), max_length=200, upload_to=IMAGE_FOLDER, blank=True, null=True,
                              default=settings.DEFAULT_PROFILE_PICTURE_URL)

    # NTNU credentials
    ntnu_username = models.CharField(_(u"NTNU-brukernavn"), max_length=10, blank=True, null=True)

    # TODO profile pictures
    # TODO checkbox for forwarding of @online.ntnu.no mail
        
    @property
    def is_member(self):
        """
        Returns true if the User object is associated with Online.
        """
        if AllowedUsername.objects.filter(username=self.ntnu_username).filter(expiration_date__gte=datetime.datetime.now()).count() > 0:
            return True
        return False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_email(self):
        return self.get_emails().filter(primary = True)[0]

    def get_emails(self):
        return Email.objects.all().filter(user = self)

    @property
    def year(self):
        today = datetime.datetime.now().date()
        started = self.started_date

        # We say that a year is 360 days incase we are a bit slower to
        # add users one year.
        year = ((today - started).days / 360) + 1

        if self.field_of_Study == 0 or self.field_of_study == 100:  # others
            return 0
        # dont return a bachelor student as 4th or 5th grade
        elif self.field_of_study == 1:  # bachelor
            if year > 3:
                return 3
            return year
        elif 9 < self.field_of_study < 30:  # 10-29 is considered master
            if year >= 2:
                return 5
            return 4
        elif self.field_of_study == 80:  # phd
            return year + 5
        elif self.field_of_study == 90:  # international
            if year == 1:
                return 1
            return 4

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _(u"brukerprofil")
        verbose_name_plural = _(u"brukerprofiler")


class Email(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="email_user")
    email = models.EmailField(_(u"epostadresse"), unique=True)
    primary = models.BooleanField(_(u"aktiv"), default=False)
    verified = models.BooleanField(_(u"verifisert"), default=False)

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _(u"epostadresse")
        verbose_name_plural = _(u"epostadresser")


class RegisterToken(models.Model):
    user = models.ForeignKey(OnlineUser, related_name="register_user")
    email = models.EmailField(_("epost"), max_length=254)
    token = models.CharField(_("token"), max_length=32)
    created = models.DateTimeField(_("opprettet dato"), editable=False, auto_now_add=True, default=datetime.datetime.now())

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        return now < self.created + valid_period 


class AllowedUsername(models.Model):
    """
    Holds usernames that are considered valid members of Online and the time they expire.
    """
    username = models.CharField(_(u"brukernavn"), max_length=10)
    registered = models.DateField(_(u"registrert"))
    note = models.CharField(_(u"notat"), max_length=100)
    description = models.TextField(_(u"beskrivelse"), blank=True, null=True)
    expiration_date = models.DateField(_(u"utløpsdato"))

    @property
    def is_active(self):
        return datetime.datetime.now() < self.expiration_date

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _("tillatt brukernavn")
        verbose_name_plural = _("tillatte brukernavn")
        ordering = ("username",)
