# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

class OnlineUser(AbstractBaseUser):
    FIELD_OF_STUDY_CHOICES = (
        (0, '--'),
        (1, 'BIT'),
        (2, 'MIT'),
        (3, 'PhD'),
        (4, 'International'),
    )
    
    # standard django user fields
    username = models.CharField(max_length=40, unique=True, db_index=True)
    email = models.EmailField(max_length=254, unique=True)

    # Online related fields
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateTimeField(_(u"startet studie"), default=datetime.now())
    compiled = models.BooleanField(_(u"kompilert"), default=False)

    # Email
    infomail = models.BooleanField(_(u"vil ha infomail"), default=True)

    # Address
    phone_number = models.CharField(_(u"telefonnummer"), max_length=20, blank=True, null=True)
    address = models.CharField(_(u"adresse"), max_length=30, blank=True, null=True)
    area_code = models.CharField(_(u"postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_(u"allergier"), blank=True, null=True)
    mark_rules = models.BooleanField(_(u"godtatt prikkeregler"), default=False)
    rfid = models.CharField(_(u"RFID"), max_length=50, blank=True, null=True)

    # TODO profile pictures
    # TODO checkbox for forwarding of @online.ntnu.no mail

    @property
    def is_online(self):
        return self.field_of_study != 0

    @property
    def year(self):
        today = datetime.now()
        started = self.started_date

        # We say that a year is 360 days incase we are a bit slower to
        # add users one year.
        year = ((today - started).days / 360) + 1

        # dont return a bachelor student as 4th or 5th grade
        if self.field_of_Study == 0:  # others
            return 0
        elif self.field_of_study == 1:  # bachelor
            if year > 3:
                return 3
            return year
        elif self.field_of_study == 2:  # master
            if year >= 2:
                return 5
            return 4
        elif self.field_of_study == 3:  # phd
            return year + 5
        elif self.field_of_study == 4:  # international
            if year == 1:
                return 1
            return 4

    def __unicode__(self):
        return username

    class Meta:
        verbose_name = _(u"brukerprofil")
        verbose_name_plural = _(u"brukerprofiler")

class RegisterToken(models.Model):
    user = models.ForeignKey(OnlineUser)
    token = models.CharField("token", max_length=32)
    created = models.DateTimeField("created", editable=False, auto_now_add=True, default=datetime.datetime.now())

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        return now < self.created + valid_period 
