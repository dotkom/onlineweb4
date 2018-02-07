# -*- coding: utf-8 -*-
from django import forms

from django.utils.translation import ugettext as _

from apps.photoalbum.models import Album, Photo

class AlbumForm(forms.Form):
	title = forms.CharField(widget=forms.TextInput(), label=_("Tittel"))
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"))    
	tags = forms.CharField(widget=forms.TextInput(), label=("Tags"))


class AlbumForm2(forms.ModelForm):
	print("AlbumForm2")
	photos_to_upload = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"), required=False)    

	class Meta(object):
		model = Album
		fields = ['title', 'photos_to_upload']


class AlbumNameForm(forms.ModelForm):
	class Meta(object):
		model = Album
		fields = ['title']


class UploadPhotosForm(forms.ModelForm):
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"), required=False)    
	class Meta(object):
		model = Album
		fields = ['photos']


class ReportPhotoForm(forms.Form):
  reason = forms.CharField(widget=forms.TextInput(), label=_("Begrunnelse"))