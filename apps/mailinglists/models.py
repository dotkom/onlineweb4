from django.db import models
from django.utils.translation import gettext as _


class MailEntity(models.Model):
    """
    This model can represent one of the following:
    1. An organization
    2. Individual person
    3. A mailinglist
    All who we are interested in having on one our our mailinglist
    """

    email = models.EmailField(verbose_name=_("E-postadresse"), unique=True)
    name = models.CharField(
        help_text=_("Fullt navn på organisasjonen eller e-postlisten"),
        verbose_name=_("Navnet på organisasjonen"),
        max_length=100,
    )
    description = models.TextField(
        help_text=_(
            "En kort beskrivelse av hva organisasjonen er, eller e-postlisten inneholder."
        ),
        verbose_name=_("Beskrivelse"),
        blank=True,
    )
    public = models.BooleanField(
        help_text=_("Hvorvidt e-posten skal være offentlig synlig"),
        verbose_name=_("Offentlig synlighet"),
        default=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("e-postentitet")
        verbose_name_plural = _("e-postentiteter")
        ordering = ["name"]


class MailGroup(models.Model):
    """
    Mailinglists used for contacting groups of related emails all at once
    """

    class Domains(models.TextChoices):
        ONLINE_NTNU_NO = "online.ntnu.no", "online.ntnu.no"
        LINJEFORENINGER_NO = "linjeforeninger.no", "linjeforeninger.no"
        ITFORENINGER_NO = "itforeninger.no", "itforeninger.no"
        TECHTALKS_NO = "techtalks.no", "techtalks.no"

    # The part before `@` is called local_part
    # Source: https://tools.ietf.org/html/rfc3696#section-3
    email_local_part = models.CharField(
        help_text=_("Navnet på e-postadresse, uten @online.ntnu.no"),
        verbose_name=_("E-postnavn"),
        max_length=50,
        unique=True,
    )
    domain = models.CharField(
        help_text=_("Domenet denne gruppen ligger under, f.eks. online.ntnu.no"),
        verbose_name=_("E-postdomenet"),
        choices=Domains.choices,
        default=Domains.ONLINE_NTNU_NO,
        max_length=50,
    )

    name = models.CharField(
        help_text=_(
            "Fullt navn på gruppen denne e-postlisten representerer, altså ikke e-postadressen"
        ),
        verbose_name=_("Navnet på gruppen"),
        max_length=100,
    )
    description = models.TextField(
        help_text=_(
            "En forklaring på hva slags entiteter gruppen skal inneholde, og hva den kan brukes til"
        ),
        verbose_name=_("Beskrivelse"),
        blank=True,
    )
    public = models.BooleanField(
        help_text=_("Hvorvidt e-postlisten skal være offentlig synlig"),
        verbose_name=_("Offentlig synlighet"),
        default=True,
    )
    members = models.ManyToManyField(
        MailEntity,
        verbose_name=_("Entiteter i denne gruppen"),
        related_name="groups",
        blank=True,
    )

    @property
    def email(self):
        return f"{self.email_local_part}@{self.domain}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("e-postliste")
        verbose_name_plural = _("e-postlister")
        ordering = ["domain", "email_local_part"]
