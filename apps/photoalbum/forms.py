# -*- coding: utf-8 -*-

from django import forms

from django.utils.translation import ugettext as _

from apps.photoalbum.models import Album

class AlbumForm(forms.Form):

	title = forms.CharField(widget=forms.TextInput(), label=_("Tittel"))
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"))    
