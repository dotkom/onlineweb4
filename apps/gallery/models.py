# -*- coding: utf-8 -*-

import os
import uuid
import watson

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

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
        return '%sx%s' % (self.image.width, self.image.height)

    class Meta(object):
        """
        UnhandledImage Metaclass
        """

        verbose_name = _(u'Ubehandlet bilde')
        verbose_name_plural = _(u'Ubehandlede bilder')
        permissions = (
            ('view_unhandledimage', _(u'View UnhandledImage')),
        )


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def unhandled_image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.image:
        instance.image.delete(False)
    if instance.thumbnail:
        instance.thumbnail.delete(False)

# Connect post_delete event with
post_delete.connect(receiver=unhandled_image_delete, dispatch_uid=uuid.uuid1(), sender=UnhandledImage)


# TODO: Introduce tags to images
class ResponsiveImage(models.Model):
    name = models.CharField(u'Navn', max_length=200, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    description = models.TextField(u'Beskrivelse', blank=True, default='', max_length=2048)
    image_original = models.FileField(u'Originalbilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_wide = models.ImageField(u'Bredformat', upload_to=gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH)
    image_lg = models.ImageField(u'LG Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_md = models.ImageField(u'MD Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_sm = models.ImageField(u'SM Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_xs = models.ImageField(u'XS Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    thumbnail = models.ImageField(u'Thumbnail', upload_to=gallery_settings.RESPONSIVE_THUMBNAIL_PATH)

    def __str__(self):
        """
        Returns the string representation of this ResponsiveImage object, which is set to be the
        LG version of the image path.

        :return: The RELATIVE path to the LG image version
        """

        return '%s%s' % (settings.MEDIA_URL, self.image_lg)

    def sizeof_total_raw(self):
        """
        Sums up the total filesize of all the different image versions.
        """

        total = self.thumbnail.size
        total += self.image_xs.size
        total += self.image_sm.size
        total += self.image_md.size
        total += self.image_lg.size
        total += self.image_wide.size
        total += self.image_original.size

        return total

    @property
    def original(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_original)

    @property
    def wide(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_wide)

    @property
    def lg(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_lg)

    @property
    def md(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_md)

    @property
    def sm(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_sm)

    @property
    def xs(self):
        return '%s%s' % (settings.MEDIA_URL, self.image_xs)

    @property
    def thumb(self):
        return '%s%s' % (settings.MEDIA_URL, self.thumbnail)

    @property
    def sizeof_total(self):
        """
        Returns a human readable string representation of the total disk usage.
        """

        total = self.sizeof_total_raw()

        return humanize_size(total)

    class Meta(object):
        """
        ResponsiveImage Metaclass
        """

        verbose_name = _(u'Responsivt Bilde')
        verbose_name_plural = _(u'Responsive Bilder')
        permissions = (
            ('view_responsiveimage', _(u'View ResponsiveImage')),
        )


# Hook up ResponsiveImage to Watson
watson.register(ResponsiveImage)


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def responsive_image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.image_original:
        instance.image_original.delete(False)
    if instance.image_wide:
        instance.image_wide.delete(False)
    if instance.image_lg:
        instance.image_lg.delete(False)
    if instance.image_md:
        instance.image_md.delete(False)
    if instance.image_sm:
        instance.image_sm.delete(False)
    if instance.image_xs:
        instance.image_xs.delete(False)
    if instance.thumbnail:
        instance.thumbnail.delete(False)

post_delete.connect(receiver=responsive_image_delete, dispatch_uid=uuid.uuid1(), sender=ResponsiveImage)
