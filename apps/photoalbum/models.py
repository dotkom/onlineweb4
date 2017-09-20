# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

IMAGE_FOLDER = "images/photo_album"

class Album(models.Model):
    title = models.CharField(_("tittel"), blank=False, null=False, max_length=50)
    photos = models.ForeignKey("Photo", null=True, blank=True)


class Photo(models.Model):
    # Path should depend on album?
    image = models.ImageField(upload_to="")
