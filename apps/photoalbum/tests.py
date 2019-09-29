# -*- coding: utf-8 -*-
"""
from django.test import TestCase
from django_dynamic_fixture import G

from apps.gallery.models import ResponsiveImage
from apps.photoalbum.models import Album

class PhotoAlbumTest(TestCase):

	#def setUp(self):
		#self.album = G(Album, title="Test album")

		#self.photo = G(Photo, album=self.album)

	def testAlbumCreation(self):
		test_title = "Test album"
		Album.objects.create(title=test_title)

		album = Album.objects.all()[0]
		self.assertEqual(album.title, test_title)

	def testPhotoCreation(self):
		album = Album.objects.all()[0]
		photo = ResponsiveImage.objects.create(photo=" ", album=album)

		self.assertEqual(photo.photo, photo_path)
		self.assertEqual(photo.album, album)

  def testAlbumTagCreation(self):
    pass

	def testPhotoUpload(self):

		pass
		# Also test that images are uploaded

	def testAlbumDeletion(self):
		pass
		# Also test that the photos are deleted


class AlbumEditFormTest(TestCase):

  def setUp(self):

	def testAlbumNameEdit(self):
		pass

	def testPhotosDeletion(self):
		pass

	def testAddPhotos(self):
		pass

  def testChangeTags(self):



"""
