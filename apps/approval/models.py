# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import FIELD_OF_STUDY_CHOICES


User = settings.AUTH_USER_MODEL


class Approval(models.Model):
    applicant = models.ForeignKey(User, verbose_name=_(u"søker"),
        related_name="applicant", editable=False)
    approver = models.ForeignKey(User, verbose_name=_(u"godkjenner"),
        related_name="approver", blank=True, null=True, editable=False)
    created = models.DateTimeField(_(u"opprettet"), auto_now_add=True)
    processed = models.BooleanField(_(u"behandlet"), default=False, editable=False)
    processed_date = models.DateTimeField(_(u"behandlet dato"), blank=True, null=True)
    approved = models.BooleanField(_(u"godkjent"), default=False, editable=False)
    message = models.TextField(_(u"melding"))


class MembershipApproval(Approval):
    new_expiry_date = models.DateField(_(u"ny utløpsdato"), blank=True, null=True)
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_(u"startet dato"), blank=True, null=True)

    def is_membership_application(self):
        if self.new_expiry_date:
            return True
        return False

    def is_fos_application(self):
        if self.field_of_study != 0 and self.started_date:
            return True
        return False

    def __unicode__(self):
        output = ""
        if self.is_fos_application():
            output = _(u"studieretningssøknad ")
        if self.is_membership_application():
            if not output:
                output = _(u"Medlemskapssøknad ")
            else:
                output = _(u"Medlemskaps- og ") + output
        if not output:
            return _(u"Tom søknad for %s") % self.applicant.get_full_name()
        return output + "for " + self.applicant.get_full_name()

    class Meta:
        verbose_name = _(u"medlemskapssøknad")
        verbose_name_plural = _(u"medlemskapssøknader")
        permissions = (
            ('view_membershipapproval', 'View membership approval'),
        )
