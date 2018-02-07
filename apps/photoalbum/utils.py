# -*- coding: utf-8 -*-


from django.contrib.auth import get_user_model

from apps.photoalbum.models import Photo, AlbumToPhoto

def upload_photos(photos, album):
	photos_list = []

	for photo in photos:
		print(photos)
		p = Photo(photo=photo)
		p.save()
		albumToPhoto = AlbumToPhoto(album=album, photo=photo)
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
		str(photo.pk) + " i album " + photo.album.title + \
		" med begrunnelse " + description 

	print("Warning prokom: " + msg)
	# Send email to prokom


