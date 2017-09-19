# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

IMAGE_FOLDER = "images/photo_album"


class Photo(models.Model):
    # Path should depend on album?
    photo_id = models.ImageField(upload_to=IMAGE_FOLDER)

class Album(models.Model):
    title = models.TextField(_("tittel"), blank=False, null=False)
    photos = models.ForeignKey(Photo)


