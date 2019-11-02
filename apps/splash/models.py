from django.db import models
from django.utils.translation import ugettext as _

from apps.events.models import Event


class AudienceGroup(models.Model):
    name = models.CharField(_("Navn"), default="", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Deltakergruppe")
        verbose_name_plural = _("Deltakergrupper")
        ordering = ("name",)


class SplashEvent(models.Model):
    title = models.CharField(_("Tittel"), max_length=100)
    content = models.TextField(_("Innhold"))
    start_time = models.DateTimeField(_("Starttid"))
    end_time = models.DateTimeField(_("Sluttid"))
    target_audience = models.ForeignKey(
        to=AudienceGroup,
        related_name="splash_events",
        verbose_name=_("Deltakergruppe"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    event = models.OneToOneField(
        to=Event,
        related_name="splash_event",
        verbose_name=_("Arrangement"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Fadderukearrangement")
        verbose_name_plural = _("Fadderukearrangementer")
        ordering = ("start_time",)
        default_permissions = ("add", "change", "delete")
