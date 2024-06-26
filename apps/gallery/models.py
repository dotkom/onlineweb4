import logging
import os

from django.conf import settings
from django.db import models
from django.db.models.fields import IntegerField
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from apps.gallery import settings as gallery_settings
from utils.helpers import humanize_size

from .constants import ImageFormat


class UnhandledImage(models.Model):
    image = models.ImageField(upload_to=gallery_settings.UNHANDLED_IMAGES_PATH)
    thumbnail = models.ImageField(upload_to=gallery_settings.UNHANDLED_THUMBNAIL_PATH)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    thumbnailSize = models.IntegerField(default=0)

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    @property
    def sizeof_original(self):
        return humanize_size(self.size)

    @property
    def sizeof_total(self):
        return humanize_size(self.size + self.size)

    @property
    def resolution(self):
        return f"{self.width}x{self.height}"

    def save(self, *args, **kwargs):
        image = self.image
        thumb = self.thumbnail
        self.size = image.size
        self.width = image.width
        self.height = image.height
        self.thumbnailSize = thumb.size
        super().save(*args, **kwargs)

    class Meta:
        """
        UnhandledImage Metaclass
        """

        verbose_name = _("Ubehandlet bilde")
        verbose_name_plural = _("Ubehandlede bilder")
        permissions = (("view_unhandledimage", _("View UnhandledImage")),)
        default_permissions = ("add", "change", "delete")


class BaseResponsiveImage(models.Model):
    """
    Base class for handling the storage part of a Responsive Image
    """

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
    timestamp = models.DateTimeField(
        auto_now_add=True, editable=False, null=False, blank=False
    )
    preset = models.CharField(
        "Format", max_length=128, choices=ImageFormat.choices, null=False, blank=False
    )
    total_size = IntegerField(default=0)

    def __str__(self):
        """
        Returns the string representation of this ResponsiveImage object, which is set to be the
        LG version of the image path.

        :return: The RELATIVE path to the LG image version
        """

        return f"{settings.MEDIA_URL}{self.image_lg}"

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

    @property
    def filename(self):
        return os.path.basename(self.image_original.name)

    @property
    def original(self):
        return f"{settings.MEDIA_URL}{self.image_original}"

    @property
    def wide(self):
        return f"{settings.MEDIA_URL}{self.image_wide}"

    @property
    def lg(self):
        return f"{settings.MEDIA_URL}{self.image_lg}"

    @property
    def md(self):
        return f"{settings.MEDIA_URL}{self.image_md}"

    @property
    def sm(self):
        return f"{settings.MEDIA_URL}{self.image_sm}"

    @property
    def xs(self):
        return f"{settings.MEDIA_URL}{self.image_xs}"

    @property
    def thumb(self):
        return f"{settings.MEDIA_URL}{self.thumbnail}"

    @property
    def sizeof_total(self):
        """
        Returns a human readable string representation of the total disk usage.
        """
        return humanize_size(self.total_size)

    def save(self, *args, **kwargs):
        total = 0
        total = self.thumbnail.size
        total += self.image_xs.size
        total += self.image_sm.size
        total += self.image_md.size
        total += self.image_lg.size
        total += self.image_wide.size
        total += self.image_original.size
        self.total_size = total
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Responsivt Bilde")
        verbose_name_plural = _("Responsive Bilder")
        permissions = (("view_responsiveimage", _("View ResponsiveImage")),)
        default_permissions = ("add", "change", "delete")
        abstract = True


class ResponsiveImage(BaseResponsiveImage):
    """
    Regular responsive images
    """

    name = models.CharField("Navn", max_length=200, null=False)
    description = models.TextField(
        "Beskrivelse", blank=True, default="", max_length=2048
    )
    photographer = models.CharField(
        "Fotograf", max_length=100, null=False, blank=True, default=""
    )
    tags = TaggableManager(
        help_text="En komma eller mellomrom-separert liste med tags."
    )
