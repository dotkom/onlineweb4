from django.db import models
from django.utils.translation import ugettext as _


class Mail(models.Model):
    """
    The email of an organization, or person whose email is on one of Online's mailinglists
    """

    email = models.EmailField(_("e-postadresse"), unique=True)
    name = models.CharField(
        help_text=_("Fullt navn på organisasjonen eller e-postlisten"), max_length=100
    )
    description = models.TextField(
        help_text=_(
            "En kort beskrivelse av hva organisasjonen er, eller e-postlisten inneholder."
        ),
        blank=True,
        null=True,
    )
    public = models.BooleanField(
        help_text=_("Hvorvidt e-posten skal være offentlig synlig"), default=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Organisasjons-e-post")
        verbose_name_plural = _("Organisasjons-e-poster")


class Mailinglist(models.Model):
    """
    Mailinglists used for contacting groups of related emails all at once
    """

    email_name = models.CharField(
        _("e-postadresse"),
        help_text=_("Navnet på e-postadresse, uten @online.ntnu.no"),
        max_length=50,
        unique=True,
    )
    name = models.CharField(help_text="Fullt navn på e-postlisten", max_length=100)
    description = models.TextField(
        help_text=_("En forklaring på hva e-postlisten skal inneholde"),
        blank=True,
        null=True,
    )
    public = models.BooleanField(
        help_text=_("Hvorvidt e-postlisten skal være offentlig synlig"), default=True
    )
    members = models.ManyToManyField(Mail, blank=True, related_name="mailinglists")

    @property
    def email(self):
        return f"{self.email_name}@online.ntnu.no"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("E-postliste")
        verbose_name_plural = _("E-postlister")
