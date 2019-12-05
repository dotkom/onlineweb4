# -*- coding: utf-8 -*-

from os import path

from chunks.models import Chunk
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.gallery.models import ResponsiveImage

THUMBNAIL_HEIGHT = 200  # Ønsket høyde på thumbnail
IMAGE_FOLDER = "images/offline"


class ProxyChunk(Chunk):
    class Meta:
        proxy = True
        verbose_name = "Informasjonstekst"
        verbose_name_plural = "Informasjonstekster"


class Issue(models.Model):
    title = models.CharField(_("tittel"), max_length=50)
    release_date = models.DateField(_("utgivelsesdato"))
    description = models.TextField(_("beskrivelse"), blank=True, null=True)
    issue = models.FileField(_("pdf"), max_length=500, upload_to=IMAGE_FOLDER)
    image = models.ForeignKey(
        to=ResponsiveImage,
        related_name="offline_issues",
        verbose_name="Forsidebilde",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def release_date_to_string(self):
        month = {
            1: "Januar",
            2: "Februar",
            3: "Mars",
            4: "April",
            5: "Mai",
            6: "Juni",
            7: "Juli",
            8: "August",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember",
        }
        return month[self.release_date.month]

    def __str__(self):
        return self.title

    @property
    def url(self):
        # TODO: url kan være feil ved prodsetting
        url = str(self.issue).replace(
            "/media/", "/var/websites/prod/onlineweb_uploads/"
        )
        url = path.join(settings.MEDIA_ROOT, url)
        return url

    class Meta:
        verbose_name = "Utgivelse"
        verbose_name_plural = "Utgivelser"
        ordering = ["-release_date"]
        permissions = (("view_issue", "View Issue"),)
        default_permissions = ("add", "change", "delete")
