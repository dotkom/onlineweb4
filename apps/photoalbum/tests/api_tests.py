# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.online_oidc_provider.test import OIDCTestCase
from apps.photoalbum.models import Album, Photo, UserTag


class AlbumTestCase(OIDCTestCase):

    def setUp(self):
        self.url = reverse('albums-list')
        self.id_url = lambda _id: reverse('albums-detail', args=[_id])

        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        self.album: Album = G(Album, published_date=self.past)
        self.public_album: Album = G(Album, published_date=self.past, public=True)

    def test_album_url_retuns_ok_without_login(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_only_see_public_albums(self):
        public_response = self.client.get(self.id_url(self.public_album.id), **self.bare_headers)
        private_response = self.client.get(self.id_url(self.album.id), **self.bare_headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_see_albums(self):
        public_response = self.client.get(self.id_url(self.public_album.id), **self.headers)
        private_response = self.client.get(self.id_url(self.album.id), **self.headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_200_OK)


class PhotoTestCase(OIDCTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        self.album: Album = G(Album, published_date=self.past)
        self.public_album: Album = G(Album, published_date=self.past, public=True)

        self.photo: Photo = G(Photo, album=self.album)
        self.public_photo: Photo = G(Photo, album=self.public_album)

    @staticmethod
    def get_list_url(album: Album):
        return reverse('album_photos-list', kwargs={'album_pk': album.pk})

    @staticmethod
    def get_detail_url(photo: Photo, album: Album = None):
        return reverse('album_photos-detail', kwargs={
            'pk': photo.pk,
            'album_pk': album.pk if album else photo.album.id,
        })

    def test_photo_url_for_public_album_returns_ok_without_login(self):
        response = self.client.get(self.get_list_url(self.public_album), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_only_see_public_photos(self):
        public_response = self.client.get(self.get_detail_url(self.public_photo), **self.bare_headers)
        private_response = self.client.get(self.get_detail_url(self.photo), **self.bare_headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_see_public_and_private_albums(self):
        public_response = self.client.get(self.get_detail_url(self.public_photo), **self.headers)
        private_response = self.client.get(self.get_detail_url(self.photo), **self.headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_200_OK)

    def test_url_for_photo_with_wrong_album_returns_not_found(self):
        response = self.client.get(self.get_detail_url(self.public_photo, self.album), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserTagsTestCase(OIDCTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        tag_content_type = ContentType.objects.get_for_model(UserTag)
        all_tag_permissions = Permission.objects.filter(content_type=tag_content_type)
        self.photo_group: Group = G(Group)
        for tag_permission in all_tag_permissions:
            self.photo_group.permissions.add(tag_permission)

        self.album: Album = G(Album, published_date=self.past)
        self.public_album: Album = G(Album, published_date=self.past, public=True)

        self.photo: Photo = G(Photo, album=self.album)
        self.public_photo: Photo = G(Photo, album=self.public_album)

        self.tag: UserTag = G(UserTag, photo=self.photo)
        self.public_tag: UserTag = G(UserTag, photo=self.public_photo)

    @staticmethod
    def get_list_url(photo: Photo, album: Album):
        return reverse('album_tags-list', kwargs={
            'photo_pk': photo.pk,
            'album_pk': album.pk,
        })

    @staticmethod
    def get_detail_url(tag: UserTag, photo: Photo = None, album: Album = None):
        return reverse('album_tags-detail', kwargs={
            'pk': tag.pk,
            'photo_pk': photo.pk if photo else tag.photo.pk,
            'album_pk': album.pk if album else tag.photo.album.id,
        })

    def test_photo_url_for_public_album_returns_ok_without_login(self):
        response = self.client.get(self.get_list_url(self.public_photo, self.public_album), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_only_see_public_photos(self):
        public_url = self.get_detail_url(self.public_tag)
        private_url = self.get_detail_url(self.tag)
        public_response = self.client.get(public_url, **self.bare_headers)
        private_response = self.client.get(private_url, **self.bare_headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_see_public_and_private_albums(self):
        public_url = self.get_detail_url(self.public_tag)
        private_url = self.get_detail_url(self.tag)
        public_response = self.client.get(public_url, **self.headers)
        private_response = self.client.get(private_url, **self.headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_200_OK)

    def test_url_for_photo_with_wrong_album_returns_not_found(self):
        response = self.client.get(self.get_detail_url(self.tag, self.public_photo, self.album), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_regular_users_cannot_create_tags(self):
        user: User = G(User)
        response = self.client.post(self.get_list_url(self.photo, self.album), {
            'user': user.id,
            'photo': self.photo.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_users_can_create_tags(self):
        self.user.is_superuser = True
        self.user.save()

        user: User = G(User)
        response = self.client.post(self.get_list_url(self.photo, self.album), {
            'user': user.id,
            'photo': self.photo.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_create_tags_when_they_get_permission(self):
        self.photo_group.user_set.add(self.user)

        user: User = G(User)
        response = self.client.post(self.get_list_url(self.photo, self.album), {
            'user': user.id,
            'photo': self.photo.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_un_authenticated_users_cannot_delete_tags(self):
        response = self.client.delete(self.get_detail_url(self.public_tag), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_users_cannot_delete_tags(self):
        response = self.client.delete(self.get_detail_url(self.tag), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_delete_tags(self):
        self.photo_group.user_set.add(self.user)

        response = self.client.delete(self.get_detail_url(self.tag), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
