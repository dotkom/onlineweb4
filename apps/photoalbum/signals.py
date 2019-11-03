# -*- coding: utf-8 -*-
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Photo
from .tasks import create_responsive_photo_task

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Photo)
def attach_missing_photo_attributes(sender, instance: Photo, **kwargs):
    if not instance.relative_id:
        instance.relative_id = instance.album.increment_photo_counter()

    if not instance.title:
        instance.title = f"{instance.album.title} #{instance.relative_id}"

    if not instance.description:
        instance.description = f"Bilde i fotoalbum, {instance}"

    if (
        instance.photographer
        and instance.photographer_name != instance.photographer.get_full_name()
    ):
        instance.photographer_name = instance.photographer.get_full_name()


@receiver(post_save, sender=Photo)
def handle_image_upload(sender, instance: Photo, created=False, **kwargs):
    if not instance.image:
        create_responsive_photo_task.delay(photo_id=instance.id)
