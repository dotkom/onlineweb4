#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User, FIELD_OF_STUDY_CHOICES


class Approval(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u"søker"), related_name="applicant")
    user = models.ForeignKey(User, verbose_name=_(u"godkjenner"), related_name="approver", blank=True, null=True)
    created = models.DateTimeField(_(u"opprettet"), auto_now_add=True)
    processed = models.BooleanField(_(u"behandlet"), default=False, editable=False)
    

class MembershipApproval(Approval):
    new_expiry_date = models.DateTimeField(_(u"ny utløpsdato"))


    class Meta:
        verbose_name = _(u"medlemskapssøknad")
        verbose_name_plural = _(u"medlemskapssøknader")

class FieldOfStudyApproval(Approval):
    field_of_study = models.SmallIntegerField(_(u"studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_(u"startet dato"))
    

    class Meta:
        verbose_name = _(u"studieretningssøknad")
        verbose_name_plural = _(u"studieretningssøknader")
