# -*- coding: utf-8 -*-

import logging
import os
import shutil
import uuid

from PIL import Image, ImageOps
from django.conf import settings as django_settings

from apps.gallery import settings as gallery_settings

ratio_x = 5
ratio_y = 6


def save_unhandled_file(uploaded_file):

    log = logging.getLogger(__name__)

    filename, extension = os.path.splitext(uploaded_file.name)

    filepath = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.UNHANDLED_IMAGES_PATH,
        '%s%s' % (uuid.uuid4(), extension.lower())
    )

    try:
        with open(filepath, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    except IOError as e:
        log.error(u'Failed to save uploaded unhandled file! "%s"' % repr(e))
        return False

    return filepath


def save_responsive_image(unhandled_image, crop_data):

    source_path = os.path.join(django_settings.MEDIA_ROOT, unhandled_image.image.name)
    destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_PATH,
        os.path.basename(unhandled_image.image.name)
    )

    crop_image(source_path, destination_path, crop_data)

    return destination_path


def copy_file(source_path, destination_path):
    shutil.copy2(source_path, destination_path)


def create_thumbnail_for_unhandled_images(unhandled_image_path):

    filename = os.path.basename(unhandled_image_path)
    thumbnail_path = os.path.join(django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH, filename)

    errors = create_thumbnail(unhandled_image_path, thumbnail_path, gallery_settings.UNHANDLED_THUMBNAIL_SIZE)

    if 'error' in errors:
        return {'error': errors['error']}
    else:
        return {'thumbnail_path': thumbnail_path}


def create_responsive_images(source_path):

    log = logging.getLogger(__name__)

    wide_destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH,
        os.path.basename(source_path)
    )
    lg_destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_LG_PATH,
        os.path.basename(source_path)
    )
    md_destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_MD_PATH,
        os.path.basename(source_path)
    )
    sm_destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_SM_PATH,
        os.path.basename(source_path)
    )
    xs_destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_XS_PATH,
        os.path.basename(source_path)
    )

    wide_status = resize_image(source_path, wide_destination_path, gallery_settings.RESPONSIVE_IMAGES_WIDE_SIZE)
    lg_status = resize_image(source_path, lg_destination_path, gallery_settings.RESPONSIVE_IMAGES_LG_SIZE)
    md_status = resize_image(source_path, md_destination_path, gallery_settings.RESPONSIVE_IMAGES_MD_SIZE)
    sm_status = resize_image(source_path, sm_destination_path, gallery_settings.RESPONSIVE_IMAGES_SM_SIZE)
    xs_stauts = resize_image(source_path, xs_destination_path, gallery_settings.RESPONSIVE_IMAGES_XS_SIZE)

    # Filter status results based on state, and log if any error
    errors = filter(
        lambda s: not s[0]['success'],
        [(wide_status, 'wide'), (lg_status, 'lg'), (md_status, 'md'), (sm_status, 'sm'), (xs_stauts, 'xs')]
    )
    for status, version in errors:
        log.error(u'Failed to resize image %s' % version)

    unhandled_thumbnail_name = os.path.basename(source_path)
    responsive_thumbnail_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_THUMBNAIL_PATH,
        unhandled_thumbnail_name
    )

    # Create a new thumbnail, since we now have cropped the image and its a different cutout from
    # the preview provided by the unhandled image
    create_thumbnail(xs_destination_path, responsive_thumbnail_path, gallery_settings.RESPONSIVE_THUMBNAIL_SIZE)


def create_thumbnail(source_image_path, destination_thumbnail_path, size):

    try:
        image = Image.open(source_image_path)
    except IOError:
        return {'success': False, 'error': 'File was not an image file, or could not be found.'}

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')

    file_name, file_extension = os.path.splitext(source_image_path)

    if not file_extension:
        return {'success': False, 'error': 'File must have an extension.'}

    try:
        # Convert our image to a thumbnail
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
    except IOError:
        return {'success': False, 'error': 'Image is truncated.'}

    quality = 90
    # Save the image to file
    # Have not tried setting file extension to png, but I guess PIL would fuck you in the ass for it
    image.save(destination_thumbnail_path, file_extension[1:], quality=quality, optimize=True)

    return {'success': True}


def resize_image(source_image_path, destination_thumbnail_path, size):
    status = _open_image_file(source_image_path)

    print status

    if not status['success']:
        return status['error']

    image = status['image']
    file_extension = status['file_extension']

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')

    image_width, image_height = image.size
    target_width, target_height = size

    image_width = _match_target(image_width, target_width)
    image_height = _match_target(image_height, target_height)

    if _validate_image_dinosaurs(image_width, image_height):
        return {'success': False, 'error': 'Image has invalid dimensions.'}

    try:
        # Convert our image to a thumbnail
        image = ImageOps.fit(image, (target_width, target_height), Image.ANTIALIAS)
    except IOError:
        return {'success': False, 'error': 'Image is truncated.'}

    quality = 90

    try:
        # Have not tried setting file extension to png, but I guess PIL would fuck you in the ass for it
        image.save(destination_thumbnail_path, file_extension[1:], quality=quality, optimize=True)
    except KeyError:
        return {'success': False, 'error': 'Unknown extension.'}
    except IOError:
        return {'success': False, 'error': 'Image could not be saved.'}

    return {'success': True}


def _open_image_file(source_image_path):
    d = {'success': True, 'error': '', 'image': None}
    try:
        d['image'] = Image.open(source_image_path)
    except IOError:
        d = {'success': False, 'error': 'File was not an image file, or could not be found.'}

    file_name, file_extension = os.path.splitext(source_image_path)

    if file_extension:
        d['file_extension'] = file_extension
    else:
        d = {'success': False, 'error': 'File must have an extension.'}
    return d


def _match_target(source, target):
    return source if source < target else target


def _validate_image_dinosaurs(width, height):
    """
    Validates the dimensions (width and height) of an image object
    :param width: width of an image
    :param height: height of an image
    :return: boolean
    """
    # Give an epsilon of 0.01 because calculations.
    return float(width) / float(height) < float(ratio_x)/float(ratio_y) - 0.01 \
        or float(width) / float(height) > float(ratio_x)/float(ratio_y) + 0.01


def crop_image(source_image_path, destination_path, crop_data):

    try:
        image = Image.open(source_image_path)
    except IOError:
        return {'success': False, 'error': "File was not an image file, or could not be found."}

    # If necessary, convert the image to RGB mode
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')

    file_name, file_extension = os.path.splitext(source_image_path)

    if not file_extension:
        return {'success': False, 'error': 'File must have an extension.'}

    crop_x = float(crop_data['x'])
    crop_y = float(crop_data['y'])
    crop_height = float(crop_data['height'])
    crop_width = float(crop_data['width'])

    image_width, image_height = image.size

    # Check all the dimension and size things \o/
    # Give an epsilon of 0.01 because calculations.
    if crop_width / crop_height < float(ratio_x)/float(ratio_y) - 0.01 or crop_width / crop_height > float(ratio_x)/float(ratio_y) + 0.01:
        return {'success': False, 'error': 'Cropping ratio was not 16:9.'}

    if (crop_x < 0) \
            or (crop_y < 0) \
            or (crop_x > image_width) \
            or (crop_y > image_height) \
            or (crop_x + crop_width > image_width) \
            or (crop_y + crop_height > image_height):

        return {'success': False, 'error': 'Crop bounds are illegal!'}

    # All is OK, crop the crop
    image = image.crop((int(crop_x), int(crop_y), int(crop_x) + int(crop_width), int(crop_y) + int(crop_height)))

    quality = 90
    # Have not tried setting file extension to png, but I guess PIL would fuck you in the ass for it
    image.save(destination_path, file_extension[1:], quality=quality, optimize=True)

    return {'success': True}


def get_unhandled_media_path(unhandled_file_path):
    return os.path.join(gallery_settings.UNHANDLED_IMAGES_PATH, os.path.basename(unhandled_file_path))


def get_unhandled_thumbnail_media_path(unhandled_thumbnail_path):
    return os.path.join(gallery_settings.UNHANDLED_THUMBNAIL_PATH, os.path.basename(unhandled_thumbnail_path))


def get_responsive_original_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_PATH, os.path.basename(responsive_path))


def get_responsive_wide_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH, os.path.basename(responsive_path))


def get_responsive_lg_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_LG_PATH, os.path.basename(responsive_path))


def get_responsive_md_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_MD_PATH, os.path.basename(responsive_path))


def get_responsive_sm_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_SM_PATH, os.path.basename(responsive_path))


def get_responsive_xs_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_XS_PATH, os.path.basename(responsive_path))


def get_responsive_thumbnail_path(responsive_path):
    return os.path.join(gallery_settings.RESPONSIVE_THUMBNAIL_PATH, os.path.basename(responsive_path))


def verify_directory_structure():
    """
    Verifies that the necessary directory structure is in place. If not, it will create them.
    :return: None
    """

    # Verify that the directories exist on current platform, create if not
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.UNHANDLED_THUMBNAIL_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_THUMBNAIL_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_XS_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_SM_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_MD_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_LG_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH)):
        logging.getLogger(__name__).info(
            u'%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH))
