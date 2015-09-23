# -*- coding: utf-8 -*-
import os

from django import forms

ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".bmp"]


class DocumentForm(forms.Form):

    file = forms.ImageField()

    def clean(self):

        if 'file' not in self.cleaned_data:
            self._errors['file'] = "File attribute missing."
            return self
        else:
            form_data = self.cleaned_data['file']

        # Because PIL is a fucking idiot
        correct_file_name = _get_correct_file_name(form_data)
        form_data.name = correct_file_name

        filename, file_extension = os.path.splitext(form_data.name.lower())

        if file_extension not in ALLOWED_FILE_TYPES:
            self._errors['file'] = "File type not allowed (jpg, jpeg, png, bmp)"

        return form_data


def _get_correct_file_name(uploaded_file):

    file_name, file_extension = os.path.splitext(uploaded_file.name)

    # PIL can actually not recognize that JPG is a JPEG, fuck all the things and hours of debugging PIL source code to find this out
    if file_extension.upper() == ".JPG":
        file_extension = ".JPEG"

    return "{0}{1}".format(file_name, file_extension)
