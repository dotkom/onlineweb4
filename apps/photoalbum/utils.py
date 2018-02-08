# -*- coding: utf-8 -*-


from django.contrib.auth import get_user_model

from apps.photoalbum.models import Photo, AlbumToPhoto
from apps.photoalbum.tasks import send_report_on_photo

def upload_photos(photos, album):
	photos_list = []

	for photo in photos:
		print(photos)
		p = Photo(photo=photo)
		p.save()
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


