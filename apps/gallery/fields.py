from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from rest_framework import fields

from .forms import ALLOWED_FILE_TYPES, get_correct_file_name
from .models import UnhandledImage
from .util import UploadImageHandler


class UnhandledImageExtensionValidator(FileExtensionValidator):

    def __init__(self, message=None, code=None):
        allowed_extensions = [ext.replace(".", "") for ext in ALLOWED_FILE_TYPES]
        super().__init__(allowed_extensions=allowed_extensions, message=message, code=code)

    def __call__(self, value: UnhandledImage):
        super().__call__(value.image)


class ImageField(fields.ImageField):
    """
    Image field that will handle supported gallery uploads and name JPG files correctly for PIL/Pillow
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file_type_validator = UnhandledImageExtensionValidator()
        self.validators.append(file_type_validator)

    def to_internal_value(self, raw_image_file: InMemoryUploadedFile):
        image_file = super().to_internal_value(raw_image_file)

        if image_file:
            image_file.name = get_correct_file_name(image_file)

            result = UploadImageHandler(image_file).status
            if result:
                return result.data

        return image_file
