# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from apps.authentication.models import FIELD_OF_STUDY_CHOICES

from django.core.mail import send_mail

User = settings.AUTH_USER_MODEL


class Approval(models.Model):
    applicant = models.ForeignKey(
        User,
        verbose_name=_("søker"),
        related_name="applicant",
        editable=False
    )
    approver = models.ForeignKey(
        User,
        verbose_name=_("godkjenner"),
        related_name="approver",
        blank=True,
        null=True,
        editable=False
    )
    created = models.DateTimeField(_("opprettet"), auto_now_add=True)
    processed = models.BooleanField(_("behandlet"), default=False, editable=False)
    processed_date = models.DateTimeField(_("behandlet dato"), blank=True, null=True)
    approved = models.BooleanField(_("godkjent"), default=False, editable=False)
    message = models.TextField(_("melding"))

    def alert_user(self):
        if self.approved:
            header_message = "Ditt medlemskap i Online er godkjent"
        else:
            header_message = "Ditt medlemskap i Online er ikke godkjent"

        email = self.applicant.get_email()
        if (not email == None):
            send_mail(
                header_message,
                header_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )


class MembershipApproval(Approval):
    new_expiry_date = models.DateField(_("ny utløpsdato"), blank=True, null=True)
    field_of_study = models.SmallIntegerField(_("studieretning"), choices=FIELD_OF_STUDY_CHOICES, default=0)
    started_date = models.DateField(_("startet dato"), blank=True, null=True)

    def is_membership_application(self):
        if self.new_expiry_date:
            return True
        return False

    def is_fos_application(self):
        if self.field_of_study != 0 and self.started_date:
            return True
        return False

    def __str__(self):
        output = ""
        if self.is_fos_application():
            output = _("studieretningssøknad ")
        if self.is_membership_application():
            if not output:
                output = _("Medlemskapssøknad ")
            else:
                output = _("Medlemskaps- og ") + output
        if not output:
            return _("Tom søknad for %s") % self.applicant.get_full_name()
        return output + "for " + self.applicant.get_full_name()

    class Meta:
        verbose_name = _("medlemskapssøknad")
        verbose_name_plural = _("medlemskapssøknader")
        permissions = (
            ('view_membershipapproval', 'View membership approval'),
        )
