from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.gallery.models import ResponsiveImage
from apps.authentication.models import OnlineGroup


class CommitteeUpdate(models.Model):
    content = models.TextField(_("melding"))
    created_at = models.DateTimeField(_("Opprettet dato"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Oppdatert dato"), auto_now_add=True)
    group = models.ForeignKey(
        to=OnlineGroup,
        on_delete=models.CASCADE,
        related_name="group_update",
        verbose_name=_("Gruppe"),
        blank=False,
        null=False,
    )