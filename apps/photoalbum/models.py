# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

IMAGE_FOLDER = "uploaded_media/images/photo_album"

class Album(models.Model):
    title = models.CharField(_("Tittel"), blank=False, null=False, max_length=50)

    def __unicode__(self):
    	return self.title

class Photo(models.Model):
    # Path should depend on album?
    photo = models.ImageField(upload_to=IMAGE_FOLDER)
    album = models.ForeignKey(Album)
	