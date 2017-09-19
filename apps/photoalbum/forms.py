# -*- coding: utf-8 -*-

from django import forms

from apps.photoalbum.models import Album

class AlbumForm(forms.ModelForm):
    class Meta(object):
        model = Album

        fields = [
            'title',
            'photos'
        ]

        widgets = {
            'photos': forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
        }

