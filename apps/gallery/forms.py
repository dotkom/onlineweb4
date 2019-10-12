# -*- coding: utf-8 -*-
import logging
import os

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".bmp"]


logger = logging.getLogger(__name__)


class ImageField(forms.ImageField):
    """
    Image field that will handle JPEG images names as JPG correctly for PIL/Pillow
    """
    def clean(self, data, initial=None):
        image_file: InMemoryUploadedFile = super().clean(data, initial)
        if image_file:
            image_file.name = _get_correct_file_name(image_file)
        return image_file


def _get_correct_file_name(uploaded_file):

    file_name, file_extension = os.path.splitext(uploaded_file.name)

    if file_extension.lower() == ".jpg":
        file_extension = ".jpeg"

    return "{0}{1}".format(file_name, file_extension)


class DocumentForm(forms.Form):
    file = ImageField()

    def clean(self):

        if 'file' not in self.cleaned_data:
            self._errors['file'] = "File attribute missing."
            return self
        else:
            form_data = self.cleaned_data['file']

        filename, file_extension = os.path.splitext(form_data.name.lower())

        if file_extension not in ALLOWED_FILE_TYPES:
            self._errors['file'] = "File type not allowed (jpg, jpeg, png, bmp)"

        return form_data
