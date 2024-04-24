from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from apps.approval import settings as approval_settings
from apps.authentication.constants import FieldOfStudyType

User = settings.AUTH_USER_MODEL


class Approval(models.Model):
    applicant = models.ForeignKey(
        User,
        verbose_name=_("søker"),
        related_name="applications",
        editable=True,
        on_delete=models.CASCADE,
    )
    approver = models.ForeignKey(
        User,
        verbose_name=_("godkjenner"),
        related_name="approved_applications",
        blank=True,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(_("opprettet"), auto_now_add=True)
    processed = models.BooleanField(_("behandlet"), default=False, editable=False)
    processed_date = models.DateTimeField(_("behandlet dato"), blank=True, null=True)
    approved = models.BooleanField(_("godkjent"), default=False, editable=False)
    message = models.TextField(_("melding"))

    class Meta:
        default_permissions = ("add", "change", "delete")


class MembershipApproval(Approval):
    new_expiry_date = models.DateField(_("ny utløpsdato"), blank=True, null=True)
    field_of_study = models.IntegerField(
        _("studieretning"),
        choices=FieldOfStudyType.choices,
        default=FieldOfStudyType.GUEST,
    )
    started_date = models.DateField(_("startet dato"), blank=True, null=True)
    documentation = models.ImageField(
        upload_to=approval_settings.DOCUMENTATION_PATH,
        blank=True,
        null=True,
        default=None,
    )

    def is_membership_application(self):
        if self.new_expiry_date:
            return True
        return False

    def is_fos_application(self):
        if self.field_of_study != 0 and self.started_date:
            return True
        return False

    def has_documentation(self):
        if self.documentation:
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
        permissions = (("view_membershipapproval", "View membership approval"),)
        default_permissions = ("add", "change", "delete")
        ordering = ("pk",)
