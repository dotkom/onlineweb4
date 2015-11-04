# -*- coding: utf-8 -*-

import logging
import os
import uuid
import watson

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
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
    image_original = models.ImageField(u'Originalbilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_wide = models.ImageField(u'Bredformat', upload_to=gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH)
    image_lg = models.ImageField(u'LG Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_md = models.ImageField(u'MD Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_sm = models.ImageField(u'SM Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_xs = models.ImageField(u'XS Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    thumbnail = models.ImageField(u'Thumbnail', upload_to=gallery_settings.RESPONSIVE_THUMBNAIL_PATH)
    photographer = models.CharField(u'Fotograf', max_length=100, null=False, blank=True, default='')
    tags = TaggableManager(help_text="En komma eller mellomrom-separert liste med tags.")

    def __str__(self):
        """
        Returns the string representation of this ResponsiveImage object, which is set to be the
        LG version of the image path.

        :return: The RELATIVE path to the LG image version
        """

        return '%s%s' % (settings.MEDIA_URL, self.image_lg)

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
            log.warning(u'Caught OSError for image file reference for ResponsiveImage %d (%s)' % (
                self.id,
                self.filename
            ))
            return False
        except IOError:
            log.warning(u'Caught OSError for image file reference for ResponsiveImage %d (%s)' % (
                self.id,
                self.filename
            ))
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
            logging.getLogger(__name__).error(u'Orphaned ResponsiveImage object: %d (%s)' % (self.id, self.filename))

        return total

    @property
    def filename(self):
        return os.path.basename(self.image_original.name)

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

# Preset our dispatch UUID, so we can re-use it in the orphan removal part
# of the post_delete signal.
resp_img_uuid = uuid.uuid1()


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def responsive_image_delete(sender, instance, **kwargs):

    log = logging.getLogger(__name__)
    filename = str(instance.image_original)

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

    # Automatically delete all related objects that for some insane reason had a ref to the
    # same image. This is bat country. Really only happens if there has been an exception
    # after file upload, after cropping is complete but before the response has been sent.

    # Start by temporarily disabling the post_delete signal, so we dont have a large branching factor of
    # delete signals. We have already pre-set the UUID used by the initial connect, so we know
    # what to disconnect.
    log.debug(u'Detaching post_delete signal before removing possible orphan ResponsiveImage')
    post_delete.disconnect(dispatch_uid=resp_img_uuid, sender=sender)

    # Next we iterate over all the responsive images and check file status. If an orphan exists, it is deleted.
    for resp_img in ResponsiveImage.objects.filter(image_original=filename):
        if not resp_img.file_status_ok():
            log.info(u'ResponsiveImage delete signal hook detected orphaned objets, deleting (ID: %d)' % resp_img.id)
            resp_img.delete()

    # Now we re-attach the post_delete signal, and issue a new UUID as dispatch ID.
    log.debug(u'Re-attaching post_delete signal for ResponsiveImage')
    post_delete.connect(receiver=responsive_image_delete, dispatch_uid=uuid.uuid1(), sender=ResponsiveImage)

# Listen for ResponsiveImage.delete() signals, so we can remove the image files accordingly.
post_delete.connect(receiver=responsive_image_delete, dispatch_uid=resp_img_uuid, sender=ResponsiveImage)
