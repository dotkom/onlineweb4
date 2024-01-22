# -*- coding: utf-8 -*-

from django import forms

from apps.dashboard.widgets import DatetimePickerInput
from apps.gallery.forms import DocumentForm
from apps.photoalbum.models import Album, Photo


class AlbumCreateOrUpdateForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ("title", "description", "published_date", "tags")

        labels = {"tags": "Tags"}

        widgets = {"published_date": DatetimePickerInput()}


class PhotoCreateForm(forms.ModelForm, DocumentForm):
    class Meta:
        model = Photo
        fields = ("file", "title", "description", "tags")
