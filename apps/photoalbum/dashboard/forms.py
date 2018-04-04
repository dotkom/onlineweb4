# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from apps.photoalbum.models import Album, Photo

class AlbumForm(forms.Form):
	title = forms.CharField(widget=forms.TextInput(), label=_("Tittel"))
	tags = forms.CharField(widget=forms.TextInput(), label=_("Tags"))
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"))    


class AlbumNameForm(forms.ModelForm):
	class Meta(object):
		model = Album
		fields = ['title']


class AlbumEditForm(forms.Form):
	print("In AlbumEditForm")
	title = forms.CharField(widget=forms.TextInput(), label=_("Tittel"))
	tags = forms.CharField(widget=forms.TextInput(), label=_("Tags"))


class UploadPhotosForm(forms.ModelForm):
	photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label=_("Bilder"), required=False)

	class Meta(object):
		model = Album
		fields = ['photos']


class TagUsersForm(forms.Form):
	users = forms.CharField(widget=forms.TextInput(), label=_("Brukere"))
