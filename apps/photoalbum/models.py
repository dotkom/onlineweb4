# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser

IMAGE_FOLDER = "images/photo_album"

class Album(models.Model):
	title = models.CharField(_("Tittel"), blank=False, null=False, max_length=50)
	#photos = models.ManyToManyField("Photo")
	tags = models.ManyToManyField("AlbumTag")
	
	def __str__(self):
		return self.title

	def get_photos(self):
		return AlbumToPhoto.objects.filter(album=self).values("photo")


class Photo(models.Model):
	# Path should depend on album?
	photo = models.ImageField(upload_to=IMAGE_FOLDER)
	#album = models.ForeignKey("Album")
	#tagged_users = models.ManyToManyField(OnlineUser, blank=True)

	def get_album(self):
		return AlbumToPhoto.objects.get(photo=self).album

	def get_tagged_users(self):
		return PhotoWithUser.objects.filter(photo=self).values("user")

		

class AlbumTag(models.Model):
	name = models.CharField(_("Navn"), blank=False, null=False, max_length=20)

	def __str__(self):
		return self.name


class AlbumToPhoto(models.Model):
	photo = models.ForeignKey(Photo)
	album = models.ForeignKey(Album)


class PhotoWithUser(models.Model):
	photo = models.ForeignKey(Photo)
	user = models.ForeignKey(OnlineUser)