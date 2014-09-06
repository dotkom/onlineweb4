#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User, FIELD_OF_STUDY_CHOICES


class Approval(models.Model):
    applicant = models.ForeignKey(User, verbose_name=_(u"søker"), related_name="applicant", editable=False)
    approver = models.ForeignKey(User, verbose_name=_(u"godkjenner"), related_name="approver", blank=True, null=True, editable=False)
    created = models.DateTimeField(_(u"opprettet"), auto_now_add=True)
    processed = models.BooleanField(_(u"behandlet"), default=False, editable=False)
    approved = models.BooleanField(_(u"godkjent"), default=False, editable=False)
    message = models.TextField(_(u"melding"))
    

class MembershipApproval(Approval):
    new_expiry_date = models.DateTimeField(_(u"ny utløpsdato"))

    def __unicode__(self):
        return _(u"Medlemskapssøknad for %s") % self.applicant.get_full_name()

    class Meta:
        verbose_name = _(u"medlemskapssøknad")
        verbose_name_plural = _(u"medlemskapssøknader")


class FieldOfStudyApproval(Approval):
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_(u"startet dato"))

    def __unicode__(self):
        return _(u"Studieretningssøknad for %s") % self.applicant.get_full_name()

    class Meta:
        verbose_name = _(u"studieretningssøknad")
        verbose_name_plural = _(u"studieretningssøknader")
