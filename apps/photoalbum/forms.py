# -*- coding: utf-8 -*-

from django import forms

from django.utils.translation import ugettext as _

from apps.photoalbum.models import Album, Photo

class AlbumForm(forms.ModelForm):

	class Meta:
		model = Album
		exclude = []


	""""
	title = forms.CharField(widget=forms.TextInput(), label=_("Tittel"))
	photos = forms.FileField(widget=forms.ClearableFileInput(), label=_("Bilder"))    

	def upload_photos(photos):
		photos = UploadImageHandler(photos)
		print("Photos: ", photos)

		for photo in photos:
			Photo.objects.create(photo)
			print("Created photo")

	def save(request):
		photos = upload_photos(request.FILES.getlist('photos'))
		#Album = Alcum.objects.create()
	""""