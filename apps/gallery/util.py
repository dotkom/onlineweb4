# -*- coding: utf-8 -*-

import os
import shutil

from PIL import Image

from apps.gallery import settings as gallery_settings


def save_unhandled_file(uploaded_file):

    filepath = os.path.join(gallery_settings.UNHANDLED_IMAGES_PATH, uploaded_file.name)

    try:
        with open(filepath, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    except Exception as exception:
        print exception
        return False

    return filepath


def copy_file(source_path, destination_path):
    shutil.copy2(source_path, destination_path)


def create_thumbnail_for_unhandled_images(unhandled_image_path):

    filename = os.path.basename(unhandled_image_path)
    thumbnail_path = os.path.join(gallery_settings.UNHANDLED_THUMBNAIL_PATH, filename)

    errors = create_thumbnail(unhandled_image_path, thumbnail_path, gallery_settings.UNHANDLED_THUMBNAIL_SIZE)
    return_value = { 'thumbnail_path': thumbnail_path, 'errors': errors }

    return return_value


def create_thumbnail(source_image_path, destination_thumbnail_path, size):

    try:
        image = Image.open(source_image_path, 'r')
    except IOError:
        return "File was not an image file, or could not be found."

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
       image = image.convert('RGB')

    file_name, file_extension = os.path.splitext(source_image_path)

    if not file_extension:
        return 'File must have an extension.'

    try:
        # Convert our image to a thumbnail
        image.thumbnail(size, Image.ANTIALIAS)
    except IOError:
        return 'Image is truncated.'

    # Save the image to file
    image.save(destination_thumbnail_path)