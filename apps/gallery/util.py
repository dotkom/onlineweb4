# -*- coding: utf-8 -*-

import logging
import os
import shutil
import uuid

from PIL import Image, ImageOps
from django.conf import settings as django_settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.gallery.models import UnhandledImage
from apps.gallery import settings as gallery_settings


class GalleryStatus(object):
    """
    Status container for gallery processes
    """

    def __init__(self, status=False, message='No message', data=None):
        """
        Constructor for the GalleryStatus object contains a success flag, message text
        and reference to a data object of some sort, if it is relevant.

        :param status: True or Fails, depending on the success of the operation in question
        :param message: A string message representing the outcome of the operation
        :param data: An optional data argument, for returning successful data, or error/exception object
        """

        self.status = status
        self.message = message
        self.data = data

    @property
    def success(self):
        return self.status

    def __bool__(self):
        return self.success

    def __str__(self):
        return 'Status: %s (%s): %s' % (self.status, self.message, self.data)


class BaseImageHandler(object):
    """
    Abstract base handler for gallery images
    """

    def __init__(self, image):
        """
        Constructor for BaseImageHandler.
        :param image: An instance of UnhandledImage, ResponsiveImage or InMemoryUploadedFile
        """

        self.image = image
        self._log = logging.getLogger(__name__)
        self.status = GalleryStatus()

    def create_thumbnail(self):
        """
        Creates a thumbnail from the current image and this object type
        :return: A GalleryStatus object
        """

        # If this object is an UploadImageHandler instance, create thumbnail for non-edited view
        if isinstance(self, UploadImageHandler):
            filename = os.path.basename(self.image)

            # Generate the full thumbnail path
            thumbnail_path = os.path.join(
                django_settings.MEDIA_ROOT,
                gallery_settings.UNHANDLED_THUMBNAIL_PATH,
                filename
            )
            thumbnail_path = os.path.abspath(thumbnail_path)

            # Generate the full path to the origin image
            original_path = os.path.join(
                django_settings.MEDIA_ROOT,
                gallery_settings.UNHANDLED_IMAGES_PATH,
                filename
            )
            original_path = os.path.abspath(original_path)

            # Generate the thumbnail and return the result
            result = self._generate_thumbnail_from_source(
                original_path,
                thumbnail_path,
                gallery_settings.UNHANDLED_THUMBNAIL_SIZE
            )

            return result

        # If this object is a ResponsiveImageHandler instance, create thumbnails for the responsive image
        elif isinstance(self, ResponsiveImageHandler):
            return GalleryStatus()
        else:
            # If we have been provided an unsupported object, return unsuccessfully
            return GalleryStatus(
                False,
                'Could not decide what thumbnail to generate, since "self" is %s' % type(self),
                None
            )

    @staticmethod
    def copy_image(from_path, to_path):
        """
        Copies an image from A to B
        :param from_path: The absolute path to the source file
        :param to_path: The absolute path to the destination file
        """

        _log = logging.getLogger(__name__)
        _log.debug('Copying image %s to %s' % (from_path, to_path))
        try:
            shutil.copy2(from_path, to_path)
        except OSError as os_error:
            _log('An OSError occurred: %s' % os_error)

    @staticmethod
    def _open_image(source):
        """
        Helper method that attempts to load an image from disk using PIL.

        :param source: The absolute path to an image stored on disk.
        :return: A GalleryStatus object with results and attached Image object as data
        """

        file_name, file_extension = os.path.splitext(source)
        if not file_extension:
            return GalleryStatus(False, 'File must have an extension', source)

        try:
            img = Image.open(source)
        except IOError as e:
            return GalleryStatus(False, 'IOError: File was not an image file, or could not be found.', e)

        # If necessary, convert the image to RGB mode
        if img.mode not in ('L', 'RGB', 'RGBA'):
            img = img.convert('RGB')

        return GalleryStatus(True, 'success', img)

    @staticmethod
    def _generate_thumbnail_from_source(source, dest, thumb_size):
        """
        Helper method that creates thumbnail to 'dest' of size 'thumb-size' given a 'source' image
        :param source: An absolute path to a source image file.
        :param dest: An absolute path to where the thumbnail should be generated.
        :param thumb_size: A tuple of the form (width, height) in pixels.
        :return: A GalleryStatus object
        """

        img = BaseImageHandler._open_image(source)
        if not img:
            logging.getLogger(__name__).error('Could not open %s' % source)
            return img
        else:
            img = img.data

        file_name, file_extension = os.path.splitext(source)
        if not file_extension:
            return GalleryStatus(False, 'File must have an extension.', source)

        try:
            # Convert our image to a thumbnail
            img = ImageOps.fit(img, thumb_size, Image.ANTIALIAS)
        except IOError as e:
            return GalleryStatus(False, 'Image is truncated.', e)

        # Save the image to file
        quality = 90
        img.save(dest, file_extension[1:], quality=quality, optimize=True)

        return GalleryStatus(True, 'success', source)

    def __bool__(self):
        """
        We override the truthness evaluation in order to quickly assess the state of the handler
        object in different parts of the system
        """

        return bool(self.status)


class UploadImageHandler(BaseImageHandler):
    """
    The ImageUploadHandler is a container encapsulating the state and workflow during file upload,
    sanitazion, initial thumbnail generation and model creation. The state of this object after
    it has completed the initialization process should be bool(self) yielding True, and self.image
    is an instance of UnhandledImage. If bool(self) is False, an error has occured and error information
    is accessible through the self.status.message and self.status.data fields.
    """

    def __init__(self, image):
        """
        Constructor accepting an instance of a generic uploaded file, or an
        UnhandledImage object from gallery models.
        :param image: Either an UnhandledImage object or an InMemoryUploadedFile object
        """

        super().__init__(image)

        # Do we already have an UnhandledImage stored in the database?
        if isinstance(image, UnhandledImage):
            self._log.debug('ImageUploadHandler instanced with %s' % image)
        # Or are we performing a new upload?
        elif isinstance(image, InMemoryUploadedFile):
            self._log.debug('ImageUploadHandler instanced with in-memory file data')

            # Handle the upload of the image
            self._handle_upload(image)
            if not self.status:
                self._log.error('Image upload failed: %s' % self.status)

        else:
            self._log.error('ImageUploadHandler instanced with non-valid type: %s' % type(image))

            raise ValueError('ImageUploadHandler can only be instanced with UnhandledImage or InMemoryUploadedFile')

    def _handle_upload(self, memory_object):
        """
        Helper method that handles the high level operations of processing the uploaded image.
        :param memory_object: A django InMemoryUploadedFile object
        """

        # Save image to disk or break early on failure
        original = self._save_in_memory_file_data(memory_object)
        if not original:
            self.status = original
            return

        # Save the path to where the image was stored
        self.image = os.path.abspath(original.data)
        self._log.debug('Unhandled file was saved at: "%s"' % self.image)

        # Generate a thumbnail image or break early on failure
        thumbnail = self.create_thumbnail()  # From superclass
        if not thumbnail:
            self._log.error('Failed to create thumbnail for %s' % self.image)
            self.status = thumbnail
            return

        self._log.debug('Creating an UnhandledImage for "%s"' % self.image)

        # Translate the relative paths to Django Media paths
        full_path = get_unhandled_media_path(os.path.abspath(original.data))
        thumb_path = get_unhandled_thumbnail_media_path(os.path.abspath(thumbnail.data))

        # Create an UnhandledImage object and save it
        self.image = UnhandledImage(image=full_path, thumbnail=thumb_path)
        self.image.save()

        # Update our status
        self._log.debug('Successfully created UnhandledImage %s' % self.image)
        self.status = GalleryStatus(True, 'success', self.image)

    def _save_in_memory_file_data(self, memory_object):
        """
        Helper method that stores data from an uploaded image from memory onto disk
        :param memory_object: A Django InMemoryUploadedFile object
        """

        # Fetch the name and extension to generate the final file path using uuid's
        filename, extension = os.path.splitext(memory_object.name)
        filepath = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.UNHANDLED_IMAGES_PATH,
            '%s%s' % (uuid.uuid4(), extension.lower())
        )
        filepath = os.path.abspath(filepath)

        self._log.debug('_save_in_memory_file_data: Attempting to store in-memory image at %s' % filepath)
        # Open a file pointer in binary mode and write the image data chunks from memory
        try:
            with open(filepath, 'wb+') as destination:
                for chunk in memory_object.chunks():
                    destination.write(chunk)
        except IOError as e:
            self._log.error('_save_in_memory_file_data: Failed to save in memory image! "%s"' % repr(e))

            return GalleryStatus(False, str(e), memory_object)

        self._log.debug('_save_in_memory_file_data: Stored in-memory image successfully')

        return GalleryStatus(True, 'success', filepath)


class ResponsiveImageHandler(BaseImageHandler):
    """
    The ImageHandler works as a container for uploaded images, and maintains
    state, file references and methods to perform all actions needed in the workflow of transitioning
    from an unedited uploaded image to the finished, cropped responsiveimage formats.
    """

    def __init__(self, image):
        super(ResponsiveImageHandler, self).__init__(image)
        if not isinstance(image, UnhandledImage):
            self._log.error('Attempt to instance ResponsiveImageHandler with non-UnhandledImage object')
            raise ValueError('ResponsiveImageHandler can only be instanced with UnhandledImage objects')

        self._config = None

    def configure(self, config):
        """
        Updates this ResponsiveImageHandler object with a new configuration dictionary, that must contain
        the appropriate crop data before transformation can occur.
        :param config: A configuration dictionary containing necessary crop data.
        """

        self._log.debug('Configuring ResponsiveImageHandler with %s' % repr(config))
        self._config = config
        self.status = self._verify_config_data()
        self._log.debug('Configuration status: %s' % self.status)

        return self.status

    def _verify_config_data(self):
        """
        Performs a self-check to verify that the currently set configuration dict (self._config) contains
        all necessary values, and that they are valid.
        """

        if not self._config:
            return GalleryStatus(False, 'Configuration dict is missing!')

        valid = 'id' in self._config
        valid &= 'preset' in self._config
        valid &= 'name' in self._config
        valid &= 'x' in self._config and 'y' in self._config
        valid &= 'width' in self._config and 'height' in self._config

        if not valid:
            return GalleryStatus(False, 'Configuration dict is missing one or more attributes', self._config)

        return GalleryStatus(valid, 'success', self._config)

    def __str__(self):
        return 'ResponsiveImageHandler: %s (Status: %s)' % (self.image, self.status)


def save_responsive_image(unhandled_image, crop_data):

    source_path = os.path.join(django_settings.MEDIA_ROOT, unhandled_image.image.name)
    destination_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_IMAGES_PATH,
        os.path.basename(unhandled_image.image.name)
    )

    crop_image(source_path, destination_path, crop_data)

    return destination_path


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
    errors = [
        s for s in [(wide_status, 'wide'), (lg_status, 'lg'), (md_status, 'md'), (sm_status, 'sm'), (xs_stauts, 'sm')]
        if s[0]['success']
    ]
    for status, version in errors:
        log.error('Failed to resize image %s' % version)

    unhandled_thumbnail_name = os.path.basename(source_path)
    responsive_thumbnail_path = os.path.join(
        django_settings.MEDIA_ROOT,
        gallery_settings.RESPONSIVE_THUMBNAIL_PATH,
        unhandled_thumbnail_name
    )

    # Create a new thumbnail, since we now have cropped the image and its a different cutout from
    # the preview provided by the unhandled image
    BaseImageHandler._generate_thumbnail_from_source(
        xs_destination_path,
        responsive_thumbnail_path,
        gallery_settings.RESPONSIVE_THUMBNAIL_SIZE
    )


def resize_image(source_image_path, destination_thumbnail_path, size):
    status = _open_image_file(source_image_path)
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
        d = {'success': False, 'error': 'IOError: File was not an image file, or could not be found.'}

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
    return float(width) / float(height) < float(16)/float(9) - 0.01 \
        or float(width) / float(height) > float(16)/float(9) + 0.01


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
    if crop_width / crop_height < float(16)/float(9) - 0.01 or crop_width / crop_height > float(16)/float(9) + 0.01:
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


# Path translation functions

def get_unhandled_media_path(unhandled_file_path):
    """
    Retrieve the relative path to an UnhandledImage in original size, provided a path to the image in any size or form.

    Example:
    >>> get_unhandled_media_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/non-edited/ac3c-f312-13f4.png'

    :param unhandled_file_path: A full or relative path to either full or thumnbail sized UnhandledImage
    :return: The relative path to the full size version of the UnhandledImage in question
    """

    return os.path.join(gallery_settings.UNHANDLED_IMAGES_PATH, os.path.basename(unhandled_file_path))


def get_unhandled_thumbnail_media_path(unhandled_thumbnail_path):
    """
    Retrieve the relative path to an UnhandledImage in thumbnail size, provided a path to the image in any size or form.

    Example:
    >>> get_unhandled_thumbnail_media_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/non-edited/thumbnails/ac3c-f312-13f4.png'

    :param unhandled_thumbnail_path: A full or relative path to either full or thumnbail sized UnhandledImage
    :return: The relative path to the thumbnail size version of the UnhandledImage in question
    """

    return os.path.join(gallery_settings.UNHANDLED_THUMBNAIL_PATH, os.path.basename(unhandled_thumbnail_path))


def get_responsive_original_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in original size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_original_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the original size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_PATH, os.path.basename(responsive_path))


def get_responsive_wide_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in wide size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_wide_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/wide/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the wide size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH, os.path.basename(responsive_path))


def get_responsive_lg_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in LG size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_lg_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/lg/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the LG size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_LG_PATH, os.path.basename(responsive_path))


def get_responsive_md_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in MD size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_md_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/md/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the MD size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_MD_PATH, os.path.basename(responsive_path))


def get_responsive_sm_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in SM size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_sm_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/sm/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the SM size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_SM_PATH, os.path.basename(responsive_path))


def get_responsive_xs_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in XS size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_xs_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/xs/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the xs size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_IMAGES_XS_PATH, os.path.basename(responsive_path))


def get_responsive_thumbnail_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in thumbnail size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_thumbnail_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/thumbnails/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the thumbnail size version of the ResponsiveImage in question
    """

    return os.path.join(gallery_settings.RESPONSIVE_THUMBNAIL_PATH, os.path.basename(responsive_path))


def verify_directory_structure():
    """
    Verifies that the necessary directory structure is in place. If not, it will create them.

    :return: None
    """

    # Verify that the directories exist on current platform, create if not
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.UNHANDLED_THUMBNAIL_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_THUMBNAIL_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_XS_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_SM_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_MD_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_LG_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH))
    if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH)):
        logging.getLogger(__name__).info(
            '%s directory did not exist, creating it...' % gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
        )
        os.makedirs(os.path.join(django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH))
