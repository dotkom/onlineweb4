# -*- coding: utf-8 -*-
import os

from django.contrib.auth import get_user_model
from django.conf import settings

from PIL import Image, ExifTags
from apps.photoalbum.models import Photo, AlbumToPhoto, AlbumTag, TagsToAlbum
from apps.photoalbum.tasks import send_report_on_photo


def upload_photos(photos, album):
	photos_list = []

	for photo in photos:
		p = Photo(photo=photo)
		p.save()

		rotate_photo(p.photo)

		albumToPhoto = AlbumToPhoto(album=album, photo=p)
		albumToPhoto.save()
		photos_list.append(p)

	return photos_list


def report_photo(description, photo, user):
	print("Description: ", description)
	try:
		user_name = user.get_full_name()
	except:
		user_name = "anonym"

	msg = user_name + " rapporterte bildet " +  \
		str(photo.pk) + " i album " + "phototitle" \
		" med begrunnelse " + description
		# photo.get_album(().title + \

	print("Warning prokom: ", msg)
	send_report_on_photo(user, photo, description)

	# Send email to prokom

def get_or_create_tags(names, album):
	names = names.split(",")
	tags = []
	for name in names: 
		tag, created = AlbumTag.objects.get_or_create(name=name)
		tag.save()
		tag_to_ablum, created= TagsToAlbum.objects.get_or_create(tag=tag, album=album)
		tags.append(tag)

	return tags

def get_tags_as_string(album):
	tags = album.get_tags()
	tags_string = ""
	for tag in tags:
		tags_string += tag.name
		if tag != tags[-1]:
			tags_string += ", "

	return tags_string

def get_next_photo(photo, album):
	photos = album.get_photos()
	enumerated_list = list(enumerate(photos))
	for i, loop_photo in enumerated_list:
		last_photo_index = enumerated_list[-1][0]
		is_last_photo = i == last_photo_index
		if loop_photo.pk == int(photo.pk) and not is_last_photo:
			next_photo = enumerated_list[i+1][1] 
			return next_photo
	return None

def get_previous_photo(photo, album):
	photos = album.get_photos()
	enumerated_list = list(enumerate(photos))
	for i, loop_photo in enumerated_list:
		is_first_photo = i == 0
		if loop_photo.pk == int(photo.pk) and not is_first_photo:
			previous_photo = enumerated_list[i-1][1]
			return previous_photo
	return None

def print_album_photo_indexs(album):
	photos = album.get_photos()
	pks = []
	for photo in photos: 
		pks.append(photo.pk)

def is_prokom(user):
	print("Checking if user is in prokom")
	return True
	#if (user.comittee == 'prokom'):
	#  return true
	#else:
	#  print("User is not in prokom")

def clear_tags_to_album(album):
	TagsToAlbum.objects.filter(album=album).delete()


def rotate_photo(photo):
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	print("Media root: ", settings.MEDIA_ROOT)
	print("Media URL: ", settings.MEDIA_URL)
	print("Photo: ", photo.url)
	filepath = "/home/doraoline/Coding/onlineweb4/uploaded_media/images/photo_album/IMG_2207_zotXi3h.JPG"

	try:
			image = Image.open(filepath)
			print("Opened image: ", image)
			for orientation in ExifTags.TAGS.keys():
				if ExifTags.TAGS[orientation] == 'Orientation':
					break
			print("Before dict")
			print(image._getexif())

			exif = dict(image._getexif().items())

			exif = {ExifTags.TAGS[k]: v
				for k, v in image._getexif().items()
				if k in ExifTags.TAGS}

			print("Orientation: ", exif)
			if exif[orientation] == 3:
				print("Rotate image 180 degrees")
				image = image.rotate(180, expand=True)
			elif exif[orientation] == 6:
				print("Rotate image 270 degrees")
				image = image.rotate(270, expand=True)
			elif exif[orientation] == 8:
				print("Rotate image 90 degrees")
				image = image.rotate(90, expand=True)
			image.save(filepath)
			image.close()
	except (AttributeError, KeyError, IndexError) as e:
		print("Exception: ", type(e), e, str(e))
		pass 
