# -*- coding: utf-8 -*-

import os
import uuid

from django.db import models
from django.db.models.signals import post_delete

from apps.gallery import settings as gallery_settings


class UnhandledImage(models.Model):
    image = models.ImageField(upload_to=gallery_settings.UNHANDLED_IMAGES_PATH)
    thumbnail = models.ImageField(upload_to=gallery_settings.UNHANDLED_THUMBNAIL_PATH)

    @property
    def filename(self):
        return os.path.basename(self.image.name)


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
    image_original = models.FileField(u'Originalbilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_lg = models.ImageField(u'LG Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_md = models.ImageField(u'MD Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_sm = models.ImageField(u'SM Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    image_xs = models.ImageField(u'XS Bilde', upload_to=gallery_settings.RESPONSIVE_IMAGES_PATH)
    thumbnail = models.ImageField(u'Thumbnail', upload_to=gallery_settings.RESPONSIVE_THUMBNAIL_PATH)


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def responsive_image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.image_original:
        instance.image_original.delete(False)
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
