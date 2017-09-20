# -*- coding: utf-8 -*-

from django import forms

from apps.photoalbum.models import Album

class AlbumForm(forms.ModelForm):
    photo_folder = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta(object):
        model = Album

        fields = [
            'title'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Tittel'})
        }

