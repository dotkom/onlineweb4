# -*- coding: utf-8 -*-
import logging
import uuid

from django.db.models.signals import post_delete

from apps.gallery.models import ResponsiveImage, UnhandledImage


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
    log.debug('Detaching post_delete signal before removing possible orphan ResponsiveImage')
    post_delete.disconnect(dispatch_uid=resp_img_uuid, sender=sender)

    # Next we iterate over all the responsive images and check file status. If an orphan exists, it is deleted.
    for resp_img in ResponsiveImage.objects.filter(image_original=filename):
        if not resp_img.file_status_ok():
            log.info('ResponsiveImage delete signal hook detected orphaned objets, deleting (ID: %d)' % resp_img.id)
            resp_img.delete()

    # Now we re-attach the post_delete signal, and issue a new UUID as dispatch ID.
    log.debug('Re-attaching post_delete signal for ResponsiveImage')
    post_delete.connect(receiver=responsive_image_delete, dispatch_uid=uuid.uuid1(), sender=ResponsiveImage)

# Listen for ResponsiveImage.delete() signals, so we can remove the image files accordingly.
post_delete.connect(receiver=responsive_image_delete, dispatch_uid=resp_img_uuid, sender=ResponsiveImage)
