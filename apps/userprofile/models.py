# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver


class UserProfile(models.Model):
    FIELD_OF_STUDY_CHOICES = (
        (0, '--'),
        (1, 'BIT'),
        (2, 'MIT'),
        (3, 'PhD'),
        (4, 'International'),
    )

    user = models.ForeignKey(User, unique=True)

    # Online related fields
    field_of_study = models.SmallIntegerField(_("studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateTimeField(_("startet studie"), default=datetime.now())
    compiled = models.BooleanField(_("kompilert"), default=False)

    # Email
    infomail = models.BooleanField(_("vil ha infomail"), default=True)

    # Address
    phone_number = models.CharField(_("telefonnummer"), max_length=20, blank=True, null=True)
    address = models.CharField(_("adresse"), max_length=30, blank=True, null=True)
    area_code = models.CharField(_("postnummer"), max_length=4, blank=True, null=True)

    # Other
    allergies = models.TextField(_("allergier"), blank=True, null=True)
    mark_rules = models.BooleanField(_("godtatt prikkeregler"), default=False)
    rfid = models.CharField(_("RFID"), max_length=50, blank=True, null=True)

    # TODO profile pictures
    # TODO checkbox for forwarding of @online.ntnu.no mail

    def save(self, *args, **kwargs):
        """
        For the post_save hook to work with django admin.
        Update the newly created UserProfile instead of trying to create
        a new one.
        """
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id  # force update instead of insert
        except UserProfile.DoesNotExist:
            pass
        models.Model.save(self, *args, **kwargs)

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
        return "for %s" % self.user.username

    class Meta:
        verbose_name = _("brukerprofil")
        verbose_name_plural = _("brukerprofiler")


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile when user is created.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
