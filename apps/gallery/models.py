# -*- coding: utf-8 -*-

import os
import uuid
import cStringIO
import shutil

from PIL import Image

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile, File
from django.db import models
from django.db.models.signals import post_delete

from apps.gallery import settings as gallerySettings


def get_thumbnail_path(instance, file_name):

    if isinstance(instance, UnhandledImage):
        print "madda"
    elif isinstance(instance, ResponsiveImage):
        print "fakka"



class ImageWithThumbnail(models.Model):

    thumbnail = models.ImageField(upload_to=get_thumbnail_path)



UNHANDLED_IMAGES_PATH = os.path.join('images', 'non-edited')
UNHANDLED_THUMBNAIL_PATH = os.path.join(UNHANDLED_IMAGES_PATH, 'thumbnails')
UNHANDLED_THUMBNAIL_SIZE = (200, 200)


class UnhandledImage(models.Model):
    image = models.ImageField(upload_to=gallerySettings.UNHANDLED_IMAGES_PATH)
    thumbnail = models.ImageField(upload_to=gallerySettings.UNHANDLED_THUMBNAIL_PATH)

    @property
    def filename(self):
        return os.path.basename(self.image.name)


    def save(self):
        self.image.upload_to = "images/"
        self.thumbnail.upload_to = "images/"
        self.image.url = "HEHEHEHHEE"
        super(UnhandledImage, self).save()

        print "helvete"

    # def save(self):
    #
    #     try:
    #         super(UnhandledImage, self).save()
    #
    #         print "HAEHAE"
    #
    #     except Exception:
    #         print "FAEN"

        # try:
        #     self.image.upload_to = 'images/'
        #     # Save the model first to get the image to disk so we can create a thumbnail
        #     super(UnhandledImage, self).save()
        #     # Create the thumbnail, the thumbnail itself will be returned in a ContentFile
        #     thumbnail_path, content_file, errors = _create_thumbnail(self.image, UNHANDLED_THUMBNAIL_PATH, UNHANDLED_THUMBNAIL_SIZE)
        #
        #     self.thumbnail.save(thumbnail_path, content_file, save=False)
        #     # Save the model once again to reflect changes on the thumbnail
        #     super(UnhandledImage, self).save()
        #
        # except:
        #     pass
        # # Close all files, because fuck locking
        # if self.image:
        #     self.image.close()
        # if self.thumbnail:
        #     self.thumbnail.close()
        # if content_file:
        #     content_file.close()
        #
        # if errors:
        #     self.delete()
        #     return errors


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def unhandled_image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.image:
        instance.image.delete(False)
    if instance.thumbnail:
        instance.thumbnail.delete(False)

# Connect post_delete event with
post_delete.connect(receiver=unhandled_image_delete, dispatch_uid=uuid.uuid1(), sender=UnhandledImage)



RESPONSIVE_IMAGES_PATH = os.path.join('images', 'responsive')
RESPONSIVE_THUMBNAIL_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'thumbnails')
RESPONSIVE_THUMBNAIL_SIZE = (200, 200)
RESPONSIVE_IMAGES_LG_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'lg')
RESPONSIVE_IMAGES_LG_SIZE = (1280, 720)
RESPONSIVE_IMAGES_MD_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'md')
RESPONSIVE_IMAGES_MD_SIZE = (1024, 576)
RESPONSIVE_IMAGES_SM_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'sm')
RESPONSIVE_IMAGES_SM_SIZE = (864, 486)
RESPONSIVE_IMAGES_XS_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'xs')
RESPONSIVE_IMAGES_XS_SIZE = (640, 360)

class ResponsiveImage(models.Model):
    image_original = models.FileField(upload_to = RESPONSIVE_IMAGES_PATH)
    image_lg = models.ImageField(upload_to = RESPONSIVE_IMAGES_PATH)
    image_md = models.ImageField(upload_to = RESPONSIVE_IMAGES_PATH)
    image_sm = models.ImageField(upload_to = RESPONSIVE_IMAGES_PATH)
    image_xs = models.ImageField(upload_to = RESPONSIVE_IMAGES_PATH)
    thumbnail = models.ImageField(upload_to = RESPONSIVE_THUMBNAIL_PATH)

    def save(self):
        try:
            # shutil.copy2(self.image_original.path, image_path)
            self.image_original.upload_to = 'images/'
            super(ResponsiveImage, self).save()

            thumbnail_path, content_file, errors = _create_thumbnail(self.image_original, RESPONSIVE_THUMBNAIL_PATH, RESPONSIVE_THUMBNAIL_SIZE)
            self.thumbnail.save(thumbnail_path, content_file, save=False)

            print "Creating lg version"
            # Create lg version
            lg_path, content_file, errors = _create_resized_image(self.image_original, RESPONSIVE_IMAGES_LG_PATH, RESPONSIVE_IMAGES_LG_SIZE)

            print "LG_PATH: " + lg_path
            self.image_lg.upload_to = "images/"
            self.image_lg.save(lg_path, content_file, save=True)

            print "Created lg version (supposedly)"

            # Save the model once again to reflect changes on the thumbnail
            super(ResponsiveImage, self).save()

        except Exception as e:
            print "ROFL"
            print e
            print "-----------------------------------"
        # Close all files, because fuck locking
        if self.image_original:
            self.image_original.close()
        if self.image_lg:
            self.image_lg.close()
        if self.image_md:
            self.image_md.close()
        if self.image_sm:
            self.image_sm.close()
        if self.image_xs:
            self.image_xs.close()
        if self.thumbnail:
            self.thumbnail.close()
        # if content_file:
        #     content_file.close()

        # if errors:
        #     self.delete()
        #     return errors


# If we delete an image, we don't want to keep the actual images
# This signal makes sure that the images along with the thumbnails are deleted from disk
def responsive_image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.image_original:
        instance.image_original.delete(False)
    if instance.image_lg:
        instance.image_lg.delete(False)
    if instance.image_md:
        instance.image_md.delete(False)
    if instance.image_sm:
        instance.image_sm.delete(False)
    if instance.image_xs:
        instance.image_xs.delete(False)
    if instance.thumbnail:
        instance.thumbnail.delete(False)

post_delete.connect(receiver=responsive_image_delete, dispatch_uid=uuid.uuid1(), sender=ResponsiveImage)


def _create_thumbnail(image_field, thumbnail_path, size):

    # Get full path of image file we're creating a thumbnail from
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_path, os.path.basename(image_field.name))

    # Open the original image in-memory to prevent locking
    image = Image.open(image_field.file, 'r')

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
       image = image.convert('RGB')

    # Because PIL is a fucking idiot, we need to load the image first
    # It will fail, and work on the second try (inside of PILs methods),
    # which is intentional. This is to prevent truncated images.
    # However, if we don't give a flying fuck, we can just do this:
    # try:
    #     image.load()
    # except:
    #     pass
    # Filebrowser will however fail loading the images stored in this way, if
    # the image is truncated, becaues it doesn't do this "hack" fuck everything shit fuck


    # Create an in-memory stream, to prevent django from storing a copy of the thumbnail
    io = cStringIO.StringIO()
    file_name, file_extension = os.path.splitext(thumbnail_path)

    if file_extension:
        file_extension = file_extension[1:]
    else:
        return None, None, 'Error: File must have an extension.'

    try:
        # Convert our image to a thumbnail
        image.thumbnail(size, Image.ANTIALIAS)
    except IOError:
        return None, None, 'Error: Image is truncated.'

    # Save the image into the in-memory stream
    image.save(io, file_extension)

    # Create an in-memory file like object with properties django can use to save our ImageField
    content_file = ContentFile(io.getvalue())

    return thumbnail_path, content_file, None


def _create_resized_image(image_field, image_path, size):


    # Get full path of image file we're creating a thumbnail from
    image_path = os.path.join(settings.MEDIA_ROOT, image_path, os.path.basename(image_field.name))
    print "Image path: " + image_path

    # Open the original image in-memory to prevent locking
    image = Image.open(image_field.file.name, 'r')

    print "Got here"

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
       image = image.convert('RGB')

    print "Got here hehe"

    # Create an in-memory stream, to prevent django from storing a copy of the thumbnail
    io = cStringIO.StringIO()
    file_name, file_extension = os.path.splitext(image_path)

    print "File name: " + file_name
    print "File extension: " + file_extension

    if file_extension:
        file_extension = file_extension[1:]
    else:
        return None, None, 'Error: File must have an extension.'

    # Convert our image to a thumbnail
    image = image.resize(size, Image.ANTIALIAS)

    # Save the image into the in-memory stream
    image.save(io, file_extension)

    # Create an in-memory file like object with properties django can use to save our ImageField
    content_file = ContentFile(io.getvalue())

    return image_path, content_file, None