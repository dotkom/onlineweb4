# -*- coding: utf-8 -*-

from django import forms

from apps.photoalbum.models import Album

class AlbumForm(forms.Form):

	title = forms.TextInput(attrs={'placeholder': 'Tittel'})
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))    
