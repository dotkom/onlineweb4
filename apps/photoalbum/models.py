# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify 
from django.utils.translation import ugettext as _
from unidecode import unidecode
from taggit.managers import TaggableManager

from apps.authentication.models import OnlineUser
from apps.gallery.models import ResponsiveImage

IMAGE_FOLDER = "images/photo_album"

class Album(models.Model):
	title = models.CharField(_("Tittel"), blank=False, null=False, max_length=50)
	tags = TaggableManager(blank=True)
	photos = models.ManyToManyField(ResponsiveImage)

	def __str__(self):
		return self.title

	@property
	def slug(self):
		return slugify(unidecode(self.title))

	@permalink
	def get_absolute_url(self):
			return 'album_detail', None, {'album_id': self.id, 'album_slug': self.slug}

	"""
	def get_photos(self):
		photo_list = AlbumToPhoto.objects.filter(album=self).values("photo")
		photos = []
		for photo_dict in photo_list:
			pk = photo_dict.get("photo")
			photo = Photo.objects.get(pk=pk)
			photos.append(photo)

		return photos

	def get_tags(self):
		print("All tags: ", TagsToAlbum.objects.all())
		tag_list = TagsToAlbum.objects.filter(album=self).values("tag")
		print("Tag_list: ", tag_list)
		tags = []
		for tags_dict in tag_list:
			print("Tag_dict: ", tags_dict)
			pk = tags_dict.get("tag")
			tag = AlbumTag.objects.get(pk=pk)
			tags.append(tag)

		return tags
	"""

class Photo(models.Model):
	# Path should depend on album?
	photo = models.ImageField(upload_to=IMAGE_FOLDER)
	
	def get_album(self):
		return AlbumToPhoto.objects.get(photo=self).album

	def get_tagged_users(self):
		user_list = UserTagToPhoto.objects.filter(photo=self).values("user")
		users = []
		for user_dict in user_list:
			pk = user_dict.get("user")
			user = OnlineUser.objects.get(pk=pk)
			users.append(user)

		return users
	
#@receiver(post_save, sender=Photo, dispatch_uid="update_photo")
#def update_photo(sender, instance, **kwargs):
##  if instance.image:
#    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#    fullpath = BASE_DIR + instance.image.url
#    rotate_photo(fullpath)

class AlbumTag(models.Model):
	name = models.CharField(_("Navn"), blank=False, null=False, max_length=20)

	def __str__(self):
		return self.name


class AlbumToPhoto(models.Model):
	photo = models.ForeignKey(Photo)
	album = models.ForeignKey(Album)


class UserTagToPhoto(models.Model):
	photo = models.ForeignKey(Photo)
	user = models.ForeignKey(OnlineUser)

class TagsToAlbum(models.Model):
	album = models.ForeignKey(Album)
	tag = models.ForeignKey(AlbumTag)