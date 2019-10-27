# -*- coding: utf-8 -*-

import logging
import os
import shutil
import uuid

from django.conf import settings as django_settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image, ImageOps

from apps.gallery import settings as gallery_settings
from apps.gallery.models import ResponsiveImage, UnhandledImage

logger = logging.getLogger(__name__)


def create_responsive_image_from_file(
    file, name: str, description: str, photographer: str, preset: str
) -> ResponsiveImage:
    uploaded_file = InMemoryUploadedFile(
        name=f"{uuid.uuid1()}.png",
        file=file,
        field_name="file",
        content_type="image/png",
        size=file.seek(0),
        charset="UTF-8",
    )
    base_image_handler = UploadImageHandler(uploaded_file)
    base_image = base_image_handler.image

    pillow_image = Image.open(base_image.image.path)
    image_width, image_height = pillow_image.size

    config = {
        "name": name,
        "description": description,
        "photographer": photographer,
        "x": 0,
        "y": 0,
        "width": image_width,
        "height": image_height,
        "scaleX": 1,
        "scaleY": 1,
        "id": base_image.id,
        "preset": preset,
    }

    responsive_image_handler = ResponsiveImageHandler(base_image)
    status = responsive_image_handler.configure(config)
    if not status:
        logger.error(f"Fatal error when creating responsive image from file")

    status = responsive_image_handler.generate()
    if not status:
        logger.error(f"Fatal error when creating responsive image from file")

    return status.data


class GalleryStatus(object):
    """
    Status container for gallery processes
    """

    def __init__(self, status=False, message="No message", data=None):
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
        return "Status: %s (%s): %s" % (self.status, self.message, self.data)


class BaseImageHandler(object):
    """
    Abstract base handler for gallery images
    """

    def __init__(self, image):
        """
        Constructor for BaseImageHandler.
        :param image: An instance of UnhandledImage, InMemoryUploadedFile
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
                filename,
            )
            thumbnail_path = os.path.abspath(thumbnail_path)

            # Generate the full path to the origin image
            original_path = os.path.join(
                django_settings.MEDIA_ROOT,
                gallery_settings.UNHANDLED_IMAGES_PATH,
                filename,
            )
            original_path = os.path.abspath(original_path)

            # Generate the thumbnail and return the result
            result = self._generate_thumbnail_from_source(
                original_path, thumbnail_path, gallery_settings.UNHANDLED_THUMBNAIL_SIZE
            )

            return result

        # If this object is a ResponsiveImageHandler instance, create thumbnails for the responsive image
        elif isinstance(self, ResponsiveImageHandler):

            filename = os.path.basename(get_absolute_path_to_original(self.image))

            # Generate the full thumbnail path for the unhandled image
            thumbnail_source = os.path.join(
                django_settings.MEDIA_ROOT,
                gallery_settings.UNHANDLED_THUMBNAIL_PATH,
                filename,
            )
            thumbnail_source = os.path.abspath(thumbnail_source)

            # Generate the full thumbnail path for the unhandled image
            thumbnail_dest = os.path.join(
                django_settings.MEDIA_ROOT,
                gallery_settings.RESPONSIVE_THUMBNAIL_PATH,
                filename,
            )
            thumbnail_dest = os.path.abspath(thumbnail_dest)

            return self._copy_file(thumbnail_source, thumbnail_dest)
        else:
            # If we have been provided an unsupported object, return unsuccessfully
            return GalleryStatus(
                False,
                'Could not decide what thumbnail to generate, since "self" is %s'
                % type(self),
                None,
            )

    @staticmethod
    def _copy_file(from_path, to_path):
        """
        Copies an image from A to B
        :param from_path: The absolute path to the source file
        :param to_path: The absolute path to the destination file
        """

        _log = logging.getLogger(__name__)
        _log.debug("Copying image %s to %s" % (from_path, to_path))
        try:
            shutil.copy2(from_path, to_path)
            return GalleryStatus(True, "sucess", to_path)
        except OSError as os_error:
            _log("An OSError occurred: %s" % os_error)
            return GalleryStatus(
                False,
                "Failed to copy image from %s to %s: %s"
                % (from_path, to_path, os_error),
                os_error,
            )

    @staticmethod
    def _open_image(source):
        """
        Helper method that attempts to load an image from disk using PIL.

        :param source: The absolute path to an image stored on disk.
        :return: A GalleryStatus object with results and attached Image object as data
        """

        file_name, file_extension = os.path.splitext(source)
        if not file_extension:
            return GalleryStatus(False, "File must have an extension", source)

        try:
            img = Image.open(source)
        except IOError as e:
            return GalleryStatus(
                False, "IOError: File was not an image file, or could not be found.", e
            )

        # If necessary, convert the image to RGB mode
        if img.mode not in ("L", "RGB", "RGBA"):
            img = img.convert("RGB")

        return GalleryStatus(True, "success", img)

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
            logging.getLogger(__name__).error("Could not open %s" % source)
            return img
        else:
            img = img.data

        file_name, file_extension = os.path.splitext(source)
        if not file_extension:
            return GalleryStatus(False, "File must have an extension.", source)

        try:
            # Convert our image to a thumbnail
            img = ImageOps.fit(img, thumb_size, Image.ANTIALIAS)
        except IOError as e:
            return GalleryStatus(False, "Image is truncated.", e)

        # Save the image to file
        img.save(
            dest,
            file_extension.replace(".", ""),
            quality=gallery_settings.THUMBNAIL_QUALITY,
            optimize=True,
        )

        return GalleryStatus(True, "success", source)

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
            self._log.debug("ImageUploadHandler instanced with %s" % image)
        # Or are we performing a new upload?
        elif isinstance(image, InMemoryUploadedFile) or isinstance(
            image, TemporaryUploadedFile
        ):
            self._log.debug(
                "ImageUploadHandler instanced with %s file data" % image.__class__
            )

            # Handle the upload of the image
            self._handle_upload(image)
            if not self.status:
                self._log.error("Image upload failed: %s" % self.status)

        else:
            self._log.error(
                "ImageUploadHandler instanced with non-valid type: %s" % type(image)
            )

            raise ValueError(
                "ImageUploadHandler can only be instanced with UnhandledImage or InMemoryUploadedFile"
            )

    def _handle_upload(self, memory_object):
        """
        Helper method that handles the high level operations of processing the uploaded image.
        :param memory_object: A django InMemoryUploadedFile object
        """

        # Save image to disk or break early on failure
        original = self._save_temp_uploaded_file_data(memory_object)
        if not original:
            self.status = original
            return

        # Save the path to where the image was stored
        self.image = os.path.abspath(original.data)
        self._log.debug('Unhandled file was saved at: "%s"' % self.image)

        # Generate a thumbnail image or break early on failure
        thumbnail = self.create_thumbnail()  # From superclass
        if not thumbnail:
            self._log.error("Failed to create thumbnail for %s" % self.image)
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
        self._log.debug("Successfully created UnhandledImage %s" % self.image)
        self.status = GalleryStatus(True, "success", self.image)

    def _save_temp_uploaded_file_data(self, memory_object):
        """
        Helper method that stores data from an uploaded image from memory onto disk
        :param memory_object: A Django InMemoryUploadedFile or TemporaryUploadedFile object
        """

        # Fetch the name and extension to generate the final file path using uuid's
        filename, extension = os.path.splitext(memory_object.name)
        filepath = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.UNHANDLED_IMAGES_PATH,
            "%s%s" % (uuid.uuid4(), extension.lower()),
        )
        filepath = os.path.abspath(filepath)

        self._log.debug(
            "_save_temp_uploaded_file_data: Attempting to store uploaded image at %s"
            % filepath
        )
        # Open a file pointer in binary mode and write the image data chunks from memory
        try:
            with open(filepath, "wb+") as destination:
                for chunk in memory_object.chunks():
                    destination.write(chunk)
        except IOError as e:
            self._log.error(
                '_save_temp_uploaded_file_data: Failed to save uploaded image! "%s"'
                % repr(e)
            )

            return GalleryStatus(False, str(e), memory_object)

        self._log.debug("_save_temp_uploaded_data: Stored uploaded image successfully")

        return GalleryStatus(True, "success", filepath)


class ResponsiveImageHandler(BaseImageHandler):
    """
    The ImageHandler works as a container for uploaded images, and maintains
    state, file references and methods to perform all actions needed in the workflow of transitioning
    from an unedited uploaded image to the finished, cropped responsiveimage formats.
    """

    def __init__(self, image):
        super(ResponsiveImageHandler, self).__init__(image)
        if not isinstance(image, UnhandledImage):
            self._log.error(
                "Attempt to instance ResponsiveImageHandler with non-UnhandledImage object"
            )
            raise ValueError(
                "ResponsiveImageHandler can only be instanced with UnhandledImage objects"
            )

        self._config = None

    def configure(self, config):
        """
        Updates this ResponsiveImageHandler object with a new configuration dictionary, that must contain
        the appropriate crop data before transformation can occur.
        :param config: A configuration dictionary containing necessary crop data.
        """

        self._log.debug("Configuring ResponsiveImageHandler with %s" % repr(config))
        self._config = config
        self.status = self._verify_config_data()
        self._log.debug("Configuration status: %s" % self.status)

        return self.status

    def generate(self):
        """
        Copy the original UnhandledImage into the "responsive" folder on disk, create a ResponsiveImage object
        for the image file, and generate cropped and downsized versions of the image for the various size profiles
        listed in Gallery "settings.py". This method must be called after ".configure()" has been invoked
        with a valid configuration file containing image metadata and cropping data.
        :return: A GalleryStatus object
        """

        if not self._config or not self.status:
            return self.status

        self._log.debug("generate: cropping %s" % self.image)

        # Crop the image
        self.status = self._crop_image()
        if not self.status:
            self._log.error(self.status)
            return self.status

        self._log.debug("generate: creating responsive image versions")

        # Create downsized versions
        self.status = self._generate_downsized_versions()
        if not self.status:
            self._log.error(self.status)
            return self.status

        responsive_image = self.status.data
        self._log.debug("generate: cleaning up")

        # Clean up
        unhandled_image_name = self.image.image.name
        self.image.delete()
        self._log.debug("UnhandledImage %s was deleted" % unhandled_image_name)

        return GalleryStatus(True, "success", responsive_image)

    def _crop_image(self):
        """
        Helper that performs the initial cropping of the image, given the current configuration.
        This method assumes that all provided crop data are valid, as this is invoked through the generate method,
        which is run post-configure.
        :return: A GalleryStatus object
        """

        # Define the paths we're going to need
        relative_source_path = self.image.image.name
        source_path = os.path.join(django_settings.MEDIA_ROOT, relative_source_path)
        file_name, file_extension = os.path.splitext(source_path)
        destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_PATH,
            os.path.basename(relative_source_path),
        )

        # Attempt to open the image with PIL
        self.status = self._open_image(source_path)
        if not self.status:
            return self.status

        # If all is good, we can reference the PIL.Image object
        image = self.status.data

        # Extract the data we need from config
        crop_x = int(self._config["x"])
        crop_y = int(self._config["y"])
        crop_height = int(self._config["height"])
        crop_width = int(self._config["width"])

        # All is OK, let PIL crop the image
        quality = gallery_settings.RESPONSIVE_IMAGE_QUALITY
        image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
        image.save(
            destination_path,
            file_extension.replace(".", ""),
            quality=quality,
            optimize=True,
        )

        self._log.debug(
            "_crop_image: successfully cropped %s"
            % get_responsive_original_path(destination_path)
        )

        return GalleryStatus(True, "success", image)

    def _resize_image(self, image, destination_path, size):
        """
        Resize an image, given a source image path, a destination path and a size tuple (x, y)
        :param image: An absolute path to the original source image
        :param destination_path: An absolute path to where the image should be saved
        :param size: An (x, y) tuple of the final size of the image in pixels
        :return: A GalleryStatus object containing the path to the resized image, or error information
        """

        # Open the file and fetch the data, or return with error information
        filename = os.path.basename(image)
        result = self._open_image(image)
        if not result:
            return result
        else:
            image = result.data

        # Extract necessary data
        file_name, file_extension = os.path.splitext(filename)
        target_width, target_height = size

        try:
            image = ImageOps.fit(image, (target_width, target_height), Image.ANTIALIAS)
        except IOError as io_error:
            self._log.error(
                "Critical error while resizing %s to %s (Image truncation)"
                % (filename, size)
            )
            return GalleryStatus(
                False, "Image source is truncated (%s)" % io_error, io_error
            )

        quality = gallery_settings.RESPONSIVE_IMAGE_QUALITY
        try:
            image.save(
                destination_path,
                file_extension.replace(".", ""),
                quality=quality,
                optimize=True,
            )
            self._log.debug(
                "Successsfully resized %s to %s"
                % (filename, (target_width, target_height))
            )
        except IOError as io_error:
            self._log.error(
                "Critical error while saving image %s: %s" % (filename, io_error)
            )
            return GalleryStatus

        return GalleryStatus(True, "success", destination_path)

    def _generate_downsized_versions(self):
        """
        Helper that generates the different responsive image versions from the cropped version of the UnhandledImage.
        This method also performs cleanup afterwards, deleting the UnhandledImage containing the original
        uploaded image, after all ResponsiveImage versions have been generated.
        :return: A GalleryStatus object
        """

        # Start by declaring all the paths the image versions will be saved to
        source_path = get_absolute_path_to_original(self.image)

        wide_destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH,
            os.path.basename(source_path),
        )
        lg_destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_LG_PATH,
            os.path.basename(source_path),
        )
        md_destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_MD_PATH,
            os.path.basename(source_path),
        )
        sm_destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_SM_PATH,
            os.path.basename(source_path),
        )
        xs_destination_path = os.path.join(
            django_settings.MEDIA_ROOT,
            gallery_settings.RESPONSIVE_IMAGES_XS_PATH,
            os.path.basename(source_path),
        )

        self._log.debug(
            "Downsizing images based on model profile: %s"
            % repr(gallery_settings.MODELS[self._config["preset"]]["sizes"])
        )

        # Resize the images based on bootstrap breakpoint sizes for each preset type
        wide = self._resize_image(
            source_path,
            wide_destination_path,
            gallery_settings.MODELS[self._config["preset"]]["sizes"]["lg"],
        )
        lg = self._resize_image(
            source_path,
            lg_destination_path,
            gallery_settings.MODELS[self._config["preset"]]["sizes"]["lg"],
        )
        md = self._resize_image(
            source_path,
            md_destination_path,
            gallery_settings.MODELS[self._config["preset"]]["sizes"]["md"],
        )
        sm = self._resize_image(
            source_path,
            sm_destination_path,
            gallery_settings.MODELS[self._config["preset"]]["sizes"]["sm"],
        )
        xs = self._resize_image(
            source_path,
            xs_destination_path,
            gallery_settings.MODELS[self._config["preset"]]["sizes"]["xs"],
        )

        # Aggregate statuses
        self.status = wide and lg and md and sm and xs

        # Create responsive thumbnail
        self.create_thumbnail()

        # Retrieve all file paths needed by the ResponsiveImage model
        original_media = get_responsive_original_path(source_path)
        wide_media = get_responsive_wide_path(source_path)
        lg_media = get_responsive_lg_path(source_path)
        md_media = get_responsive_md_path(source_path)
        sm_media = get_responsive_sm_path(source_path)
        xs_media = get_responsive_xs_path(source_path)
        thumbnail = get_responsive_thumbnail_path(source_path)

        # Create and save the actual ResponsiveImage object
        resp_image = ResponsiveImage(
            name=self._config["name"],
            description=self._config["description"],
            photographer=self._config["photographer"],
            image_original=original_media,
            image_lg=lg_media,
            image_md=md_media,
            image_sm=sm_media,
            image_xs=xs_media,
            image_wide=wide_media,
            thumbnail=thumbnail,
        )
        resp_image.save()

        # If we had any errors during any of the resizing operations, we let the ResponsiveImage clean the disk
        # for orphaned images
        if not self.status:
            self._log.debug(
                "An error occured during responsive image generation, performing cleanup"
            )
            resp_image.delete()
            return self.status

        return GalleryStatus(True, "success", resp_image)

    def _verify_config_data(self):
        """
        Performs a self-check to verify that the currently set configuration dict (self._config) contains
        all necessary values, and that they are valid.
        """

        if not self._config:
            return GalleryStatus(False, "Configuration dict is missing!")

        required = {"id", "preset", "name", "description", "x", "y", "width", "height"}
        provided = set(self._config.keys())
        valid = required == required & provided

        if not valid:
            missing = required - provided
            return GalleryStatus(
                False,
                "Configuration is missing the following attributes %s" % missing,
                self._config,
            )

        preset = self._config["preset"]
        anchor = (self._config["x"], self._config["y"])
        size = (self._config["width"], self._config["height"])
        max_size = (
            self.image.image.width,
            self.image.image.height,
        )  # self.image is an UnhandledImage object

        # Verify that the selected preset from the client exists
        if preset in gallery_settings.MODELS:
            model = gallery_settings.MODELS[preset]
        else:
            return GalleryStatus(False, 'Config contained illegal value for "preset"')

        min_size = (model["min_width"], model["min_height"])

        # Do bounds check on the provided data from the cropper.js front-end
        bounds_status = check_crop_bounds(anchor, size, min_size, max_size)
        if not bounds_status:
            return bounds_status

        # If the preset uses fixed aspect ratio, verify that the provided crop data conforms to the aspect ratio
        if model["aspect_ratio"]:
            aspect_ratio_status = check_aspect_ratio(
                size, (model["aspect_ratio_x"], model["aspect_ratio_y"])
            )
            if not aspect_ratio_status:
                return aspect_ratio_status

        return GalleryStatus(valid, "success", self._config)

    def __str__(self):
        return "ResponsiveImageHandler: %s (Status: %s)" % (self.image, self.status)


# Support functions


def check_crop_bounds(crop_anchor, crop_size, min_size, max_size):
    """
    Check whether or not the crop bounds exceed the image size
    :param crop_anchor: An (x, y) tuple containing the top-left anchor of the crop
    :param crop_size: An (x, y) tuple containing the width and height of the crop
    :param min_size: An (x, y) tuple containint the minimum width and height defined by for example a preset
    :param max_size: An (x, y) tuple containing the width and height of the original image
    :return: A GalleryStatus object
    """

    x, y = map(int, crop_anchor)
    width, height = map(int, crop_size)
    min_width, min_height = map(int, min_size)
    max_width, max_height = map(int, max_size)

    valid = x >= 0 and y >= 0
    valid &= width > 0 and height > 0
    valid &= width >= min_width and height >= min_height
    valid &= max_width > 0 and max_height > 0
    valid &= width <= max_width and height <= max_height
    valid &= x + width <= max_width and y + height <= max_height

    if not valid:
        return GalleryStatus(
            False,
            "The provided crop attributes provided out of bounds values",
            (crop_anchor, crop_size),
        )

    return GalleryStatus(True, "success")


def check_aspect_ratio(size, aspect_ratio):
    """
    Checks whether a specified image size conforms to a given aspect ratio.
    :param size: An (x, y) tuple in pixels
    :param aspect_ratio: An (x, y) tuple
    :return: A GalleryStatus object
    """

    epsilon = 0.01

    width, height = map(int, size)
    aspect_x, aspect_y = map(int, aspect_ratio)

    actual = width / height
    given = aspect_x / aspect_y

    valid = actual - given < epsilon
    if not valid:
        return GalleryStatus(
            False,
            "The provided size and aspect ratio did not match",
            (size, aspect_ratio),
        )

    return GalleryStatus(True, "success")


# Path translation functions


def get_absolute_path_to_original(image):
    """
    Returns the absolute path to the original version of an UnhandledImage or ResponsiveImage object
    :param image: An UnhandledImage or Responsive image instance
    :return: An absolute path to an image file on disk
    """

    path = django_settings.MEDIA_ROOT
    if isinstance(image, UnhandledImage):
        path = os.path.abspath(
            os.path.join(django_settings.MEDIA_ROOT, image.image.name)
        )
    elif isinstance(image, ResponsiveImage):
        path = os.path.abspath(
            os.path.join(django_settings.MEDIA_ROOT, image.image_original.name)
        )

    return path


def get_unhandled_media_path(unhandled_file_path):
    """
    Retrieve the relative path to an UnhandledImage in original size, provided a path to the image in any size or form.

    Example:
    >>> get_unhandled_media_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/non-edited/ac3c-f312-13f4.png'

    :param unhandled_file_path: A full or relative path to either full or thumnbail sized UnhandledImage
    :return: The relative path to the full size version of the UnhandledImage in question
    """

    return os.path.join(
        gallery_settings.UNHANDLED_IMAGES_PATH, os.path.basename(unhandled_file_path)
    )


def get_unhandled_thumbnail_media_path(unhandled_thumbnail_path):
    """
    Retrieve the relative path to an UnhandledImage in thumbnail size, provided a path to the image in any size or form.

    Example:
    >>> get_unhandled_thumbnail_media_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/non-edited/thumbnails/ac3c-f312-13f4.png'

    :param unhandled_thumbnail_path: A full or relative path to either full or thumnbail sized UnhandledImage
    :return: The relative path to the thumbnail size version of the UnhandledImage in question
    """

    return os.path.join(
        gallery_settings.UNHANDLED_THUMBNAIL_PATH,
        os.path.basename(unhandled_thumbnail_path),
    )


def get_responsive_original_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in original size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_original_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the original size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_PATH, os.path.basename(responsive_path)
    )


def get_responsive_wide_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in wide size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_wide_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/wide/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the wide size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH, os.path.basename(responsive_path)
    )


def get_responsive_lg_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in LG size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_lg_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/lg/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the LG size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_LG_PATH, os.path.basename(responsive_path)
    )


def get_responsive_md_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in MD size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_md_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/md/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the MD size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_MD_PATH, os.path.basename(responsive_path)
    )


def get_responsive_sm_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in SM size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_sm_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/sm/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the SM size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_SM_PATH, os.path.basename(responsive_path)
    )


def get_responsive_xs_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in XS size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_xs_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/xs/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the xs size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_IMAGES_XS_PATH, os.path.basename(responsive_path)
    )


def get_responsive_thumbnail_path(responsive_path):
    """
    Retrieve the relative path to a ResponsiveImage in thumbnail size, provided a path to the image in any size or form.

    Example:
    >>> get_responsive_thumbnail_path('/some/path/to/img/ac3c-f312-13f4.png')
    'images/responsive/thumbnails/ac3c-f312-13f4.png'

    :param responsive_path: A full or relative path to any size version of a ResponsiveImage
    :return: The relative path to the thumbnail size version of the ResponsiveImage in question
    """

    return os.path.join(
        gallery_settings.RESPONSIVE_THUMBNAIL_PATH, os.path.basename(responsive_path)
    )


def verify_directory_structure():
    """
    Verifies that the necessary directory structure is in place. If not, it will create them.

    :return: None
    """

    # Verify that the directories exist on current platform, create if not
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.UNHANDLED_THUMBNAIL_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.UNHANDLED_THUMBNAIL_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_THUMBNAIL_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_THUMBNAIL_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_IMAGES_XS_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_XS_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_IMAGES_SM_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_SM_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_IMAGES_MD_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_MD_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_IMAGES_LG_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_LG_PATH
            )
        )
    if not os.path.exists(
        os.path.join(
            django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
        )
    ):
        logging.getLogger(__name__).info(
            "%s directory did not exist, creating it..."
            % gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
        )
        os.makedirs(
            os.path.join(
                django_settings.MEDIA_ROOT, gallery_settings.RESPONSIVE_IMAGES_WIDE_PATH
            )
        )
