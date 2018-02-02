# -*- coding: utf-8 -*-

def upload_photos(photos, album):
	photos_list = []

	for photo in photos:
		print(photos)
		p = Photo(photo=photo, album=album)
		p.save()
		photos_list.append(p)

	return photos_list