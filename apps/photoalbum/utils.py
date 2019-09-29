# -*- coding: utf-8 -*-

from apps.authentication.models import OnlineUser
from apps.gallery.models import ResponsiveImage, UnhandledImage
from apps.photoalbum.models import UserTag
from apps.photoalbum.tasks import send_report_on_photo


def report_photo(description, photo, user):
    send_report_on_photo(user, photo, description)


def get_next_photo(photo, album):
    photos = album.get_photos()
    enumerated_list = list(enumerate(photos))
    for i, loop_photo in enumerated_list:
        last_photo_index = enumerated_list[-1][0]
        is_last_photo = i == last_photo_index
        if loop_photo.pk == int(photo.pk) and not is_last_photo:
            next_photo = enumerated_list[i + 1][1]
            return next_photo
    return None


def get_previous_photo(photo, album):
    photos = album.get_photos()
    enumerated_list = list(enumerate(photos))
    for i, loop_photo in enumerated_list:
        is_first_photo = i == 0
        if loop_photo.pk == int(photo.pk) and not is_first_photo:
            previous_photo = enumerated_list[i - 1][1]
            return previous_photo
    return None


def print_album_photo_indexs(album):
    photos = album.get_photos()
    pks = []
    for photo in photos:
        pks.append(photo.pk)


def get_photos_from_form(form):
    pks = form['photos']

    pks_list = pks.split(',')
    photos = []
    for pk in pks_list:
        photo = UnhandledImage.objects.get(pk)
        photos.append(photo)

    return photos


def get_photos_to_album(album_title):
    photos = ResponsiveImage.objects.filter(name=album_title)
    return photos


def tag_users(users, photo):
    user_names = users.split(",")

    for name in user_names:
        user = OnlineUser.objects.get(username=name)
        UserTag.objects.get_or_create(user=user, photo=photo)
