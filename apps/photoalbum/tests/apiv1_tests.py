# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.online_oidc_provider.test import OIDCTestCase
from apps.photoalbum.models import Album, Photo, UserTag


def add_content_type_permission_to_group(group: Group, model):
    content_type = ContentType.objects.get_for_model(model)
    all_permissions = Permission.objects.filter(content_type=content_type)
    for tag_permission in all_permissions:
        group.permissions.add(tag_permission)


def create_uploadable_file(name: str, static_location: str, content_type: str):
    static_dir = f"{settings.PROJECT_ROOT_DIRECTORY}/files/static"
    file = open(f"{static_dir}/{static_location}", "rb")
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type=content_type,
    )


class AlbumTestCase(OIDCTestCase):

    def setUp(self):
        self.url = reverse("albums-list")
        self.id_url = lambda _id: reverse("albums-detail", args=[_id])

        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        self.photo_group: Group = G(Group)
        add_content_type_permission_to_group(self.photo_group, Album)

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

    def test_only_permitted_user_can_see_unpublished_albums(self):
        unpublished_album = G(Album, published_date=self.future)

        response = self.client.get(self.id_url(unpublished_album.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.photo_group.user_set.add(self.user)

        response = self.client.get(self.id_url(unpublished_album.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_filters_work(self):
        response = self.client.get(self.url, {
            "public": True,
        }, **self.headers)
        album_ids = [album.get("id") for album in response.json().get("results")]
        self.assertNotIn(self.album.id, album_ids)

        response = self.client.get(self.url, **self.headers)
        album_ids = [album.get("id") for album in response.json().get("results")]
        self.assertIn(self.album.id, album_ids)

    def test_regular_user_cannot_create_albums(self):
        response = self.client.post(self.url, {
            "title": "Immball 2019",
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_user_can_create_albums(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.post(self.url, {
            "title": "Immball 2019",
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permitted_user_can_update_albums(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.patch(self.id_url(self.public_album.id), {
            "title": "Åre 2020",
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permitted_user_can_delete_albums(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.delete(self.id_url(self.public_album.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PhotoTestCase(OIDCTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        self.photo_group: Group = G(Group)
        add_content_type_permission_to_group(self.photo_group, Photo)

        self.album: Album = G(Album, published_date=self.past)
        self.public_album: Album = G(Album, published_date=self.past, public=True)

        self.photo: Photo = G(Photo, album=self.album)
        self.public_photo: Photo = G(Photo, album=self.public_album)

    @staticmethod
    def get_list_url():
        return reverse("album_photos-list")

    @staticmethod
    def get_detail_url(photo: Photo):
        return reverse("album_photos-detail", args=[photo.pk])

    @staticmethod
    def get_upload_url(album: Album):
        return reverse("albums-upload", args=[album.pk])

    @property
    def form_data_headers(self):
        self.headers.pop("content_type")
        return self.headers.copy()

    def get_uploadable_static_file(self):
        return create_uploadable_file(
            name="åre.jpeg",
            content_type="image/jpeg",
            static_location="img/are.JPG",
        )

    def test_photo_url_for_public_album_returns_ok_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

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

    def test_only_permitted_user_can_see_unpublished_photos(self):
        unpublished_album = G(Album, published_date=self.future)
        unpublished_photo = G(Photo, album=unpublished_album)

        response = self.client.get(self.get_detail_url(unpublished_photo), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.photo_group.user_set.add(self.user)

        response = self.client.get(self.get_detail_url(unpublished_photo), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_photos(self):
        response = self.client.post(self.get_list_url(), {
            "album": self.album.id,
            "raw_image": self.get_uploadable_static_file(),
        }, **self.form_data_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_user_can_create_photos(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.post(self.get_list_url(), {
            "album": self.album.id,
            "raw_image": self.get_uploadable_static_file(),
        }, **self.form_data_headers, )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        photo = Photo.objects.get(pk=response.json().get("id"))
        self.assertEqual(photo.photographer, self.user)
        self.assertIsNotNone(photo.title)
        self.assertIsNotNone(photo.image)

    def test_cannot_create_photo_without_upload(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.post(self.get_list_url(), {
            "album": self.album.id,
        }, **self.form_data_headers, )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("raw_image"), ["Ingen fil ble sendt."])

    def test_user_cannot_upload_wrong_image_format(self):
        unsupported_file = create_uploadable_file(
            name="nyan.gif",
            content_type="image/gif",
            static_location="img/403nyan.gif",
        )
        self.photo_group.user_set.add(self.user)
        response = self.client.post(self.get_list_url(), {
            "album": self.album.id,
            "raw_image": unsupported_file,
        }, **self.form_data_headers)

        self.assertIn("Filendelsen 'gif' er ikke tillatt.", response.json().get("raw_image")[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_permitted_user_can_update_photos(self):
        self.photo_group.user_set.add(self.user)
        new_title = "Bilde av Åreturen"

        response = self.client.patch(self.get_detail_url(self.photo), {
            "title": new_title,
        }, **self.headers)

        self.photo.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.photo.title, response.json().get("title"))

    def test_permitted_user_can_delete_photos(self):
        self.photo_group.user_set.add(self.user)
        response = self.client.delete(self.get_detail_url(self.photo), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UserTagsTestCase(OIDCTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.past = self.now - timezone.timedelta(days=1)
        self.future = self.now + timezone.timedelta(days=1)

        self.photo_group: Group = G(Group)
        add_content_type_permission_to_group(self.photo_group, UserTag)

        self.album: Album = G(Album, published_date=self.past)
        self.public_album: Album = G(Album, published_date=self.past, public=True)

        self.photo: Photo = G(Photo, album=self.album)
        self.public_photo: Photo = G(Photo, album=self.public_album)

        self.tag: UserTag = G(UserTag, photo=self.photo)
        self.public_tag: UserTag = G(UserTag, photo=self.public_photo)

    @staticmethod
    def get_list_url():
        return reverse("album_tags-list")

    @staticmethod
    def get_detail_url(tag: UserTag):
        return reverse("album_tags-detail", args=[tag.pk])

    def test_photo_url_for_public_tags_returns_ok_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_only_see_public_tags(self):
        public_url = self.get_detail_url(self.public_tag)
        private_url = self.get_detail_url(self.tag)
        public_response = self.client.get(public_url, **self.bare_headers)
        private_response = self.client.get(private_url, **self.bare_headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_see_public_and_private_tags(self):
        public_url = self.get_detail_url(self.public_tag)
        private_url = self.get_detail_url(self.tag)
        public_response = self.client.get(public_url, **self.headers)
        private_response = self.client.get(private_url, **self.headers)

        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_response.status_code, status.HTTP_200_OK)

    def test_only_permitted_user_can_see_unpublished_tags(self):
        unpublished_album = G(Album, published_date=self.future)
        unpublished_photo = G(Photo, album=unpublished_album)
        unpublished_tag = G(UserTag, photo=unpublished_photo)

        response = self.client.get(self.get_detail_url(unpublished_tag), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.photo_group.user_set.add(self.user)

        response = self.client.get(self.get_detail_url(unpublished_tag), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_users_cannot_create_tags(self):
        user: User = G(User)
        response = self.client.post(self.get_list_url(), {
            "user": user.id,
            "photo": self.photo.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_users_can_create_tags(self):
        self.user.is_superuser = True
        self.user.save()

        user: User = G(User)
        response = self.client.post(self.get_list_url(), {
            "user": user.id,
            "photo": self.photo.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_create_tags_when_they_get_permission(self):
        self.photo_group.user_set.add(self.user)

        user: User = G(User)
        response = self.client.post(self.get_list_url(), {
            "user": user.id,
            "photo": self.photo.id,
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
