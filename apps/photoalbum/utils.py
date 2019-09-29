# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from PIL import ExifTags, Image

from apps.authentication.models import OnlineUser
from apps.gallery.models import ResponsiveImage
from apps.photoalbum.models import Album
from apps.photoalbum.tasks import send_report_on_photo


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

def get_photos_from_form(form):
  print("get_photos_from_form")
  pks = form['photos']
  #print(pks)

  pks_list = pks.split(',')
  photos = []
  for pk in pks_list:
    photo = UnhandledImage.get(pk)
    photos.append(photo)
  
  #photos = [ResponsiveImage.objects.get(pk=1), ResponsiveImage.objects.get(pk=2)]
  return photos

def get_photos_to_album(album_title):
  photos = ResponsiveImage.objects.filter(name=album_title)
  return photos

"""
def tag_users(users, photo):
	print("In tag users")
	print("Uses: ", users)
	user_names = users.split(",")

	for name in user_names: 
		print("Name: ", name)
		user = OnlineUser.objects.get(username=name)
		print(user)

		user_tag_to_photo, created= UserTagToPhoto.objects.get_or_create(user=user, photo=photo)
		
		print("User tagged in photo: ", user_tag_to_photo)
"""
