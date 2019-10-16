# -*- coding: utf-8 -*-

import logging
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager

from apps.gallery import settings as gallery_settings
from utils.helpers import humanize_size


class UnhandledImage(models.Model):
    image = models.ImageField(upload_to=gallery_settings.UNHANDLED_IMAGES_PATH)
    thumbnail = models.ImageField(upload_to=gallery_settings.UNHANDLED_THUMBNAIL_PATH)

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    @property
    def sizeof_original(self):
        return humanize_size(self.image.size)

    @property
    def sizeof_total(self):
        return humanize_size(self.image.size + self.thumbnail.size)

    @property
    def resolution(self):
        return "%sx%s" % (self.image.width, self.image.height)

    class Meta:
        """
        UnhandledImage Metaclass
        """

        verbose_name = _("Ubehandlet bilde")
        verbose_name_plural = _("Ubehandlede bilder")
        permissions = (("view_unhandledimage", _("View UnhandledImage")),)
        default_permissions = ("add", "change", "delete")


class ResponsiveImage(models.Model):
    name = models.CharField("Navn", max_length=200, null=False)
    timestamp = models.DateTimeField(
        auto_now_add=True, editable=False, null=False, blank=False
    )
    description = models.TextField(
        "Beskrivelse", blank=True, default="", max_length=2048
    )
    image_original = models.ImageField(
        "Originalbilde", upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH
    )
    image_wide = models.ImageField(
        "Bredformat", upload_to=gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
    )
    image_lg = models.ImageField(
        "LG Bilde", upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH
    )
    image_md = models.ImageField(
        "MD Bilde", upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH
    )
    image_sm = models.ImageField(
        "SM Bilde", upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH
    )
    image_xs = models.ImageField(
        "XS Bilde", upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH
    )
    thumbnail = models.ImageField(
        "Thumbnail", upload_to=gallery_settings.RESPONSIVE_THUMBNAIL_PATH
    )
    photographer = models.CharField(
        "Fotograf", max_length=100, null=False, blank=True, default=""
    )
    tags = TaggableManager(
        help_text="En komma eller mellomrom-separert liste med tags."
    )

    def __str__(self):
        """
        Returns the string representation of this ResponsiveImage object, which is set to be the
        LG version of the image path.

        :return: The RELATIVE path to the LG image version
        """

        return "%s%s" % (settings.MEDIA_URL, self.image_lg)

    def file_status_ok(self):
        """
        Iterates through all the ImageField references, attempting to trigger either an OSError or IOError.

        :return: True if all files are present and correct, False otherwise
        """

        log = logging.getLogger(__name__)

        try:
            assert self.thumbnail.width is not None
            assert self.image_original.width is not None
            assert self.image_wide.width is not None
            assert self.image_lg.width is not None
            assert self.image_md.width is not None
            assert self.image_sm.width is not None
            assert self.image_xs.width is not None
        except OSError:
            log.warning(
                "Caught OSError for image file reference for ResponsiveImage %d (%s)"
                % (self.id, self.filename)
            )
            return False

        return True

    def sizeof_total_raw(self):
        """
        Sums up the total filesize of all the different image versions.
        """

        total = 0
        try:
            total = self.thumbnail.size
            total += self.image_xs.size
            total += self.image_sm.size
            total += self.image_md.size
            total += self.image_lg.size
            total += self.image_wide.size
            total += self.image_original.size
        except OSError:
            logging.getLogger(__name__).error(
                "Orphaned ResponsiveImage object: %d (%s)" % (self.id, self.filename)
            )

        return total

    @property
    def filename(self):
        return os.path.basename(self.image_original.name)

    @property
    def original(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_original)

    @property
    def wide(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_wide)

    @property
    def lg(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_lg)

    @property
    def md(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_md)

    @property
    def sm(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_sm)

    @property
    def xs(self):
        return "%s%s" % (settings.MEDIA_URL, self.image_xs)

    @property
    def thumb(self):
        return "%s%s" % (settings.MEDIA_URL, self.thumbnail)

    @property
    def sizeof_total(self):
        """
        Returns a human readable string representation of the total disk usage.
        """

        total = self.sizeof_total_raw()

        return humanize_size(total)

    class Meta:
        """
        ResponsiveImage Metaclass
        """

        verbose_name = _("Responsivt Bilde")
        verbose_name_plural = _("Responsive Bilder")
        permissions = (("view_responsiveimage", _("View ResponsiveImage")),)
        default_permissions = ("add", "change", "delete")
