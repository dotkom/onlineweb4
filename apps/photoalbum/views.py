# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.utils.translation import ugettext as _

from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from django import forms

from django.db import models

from apps.gallery.util import UploadImageHandler
from apps.gallery.models import ResponsiveImage

from apps.photoalbum.utils import report_photo, get_tags_as_string, get_previous_photo, get_next_photo, is_prokom, clear_tags_to_album
from apps.photoalbum.models import Album
from apps.photoalbum.forms import ReportPhotoForm
from django_filters import FilterSet, Filter, CharFilter
from apps.photoalbum.decorators import prokom_required
from apps.photoalbum import utils

class AlbumsListView(ListView):
	model = Album
	template_name = 'photoalbum/index.html'

	def get(self, request, *args, **kwargs):
		filter = AlbumFilter(request.GET, queryset=Album.objects.all())
		
		return render(request, 'photoalbum/index.html', {'filter': filter})

class AlbumFilter(FilterSet):

	def filter_keyword(self, queryset, value):
		queryset = []
		if value != "":
			list = value.split(" ")
			try:  
				for album in Album.objects.all():
					for word in list:
						# If word is in title
						if word.lower() in album.title.lower():
							queryset.append(album)
						else:
							try:
								tags = album.tags
								if tag != None and tag in tags():
									queryset.append(album)
							except Exception:
								print("Tag does not exist")
			except Exception as e:
				queryset = Album.objects.all()
		else:
			queryset = Album.objects.all()

		return queryset

	title = CharFilter(label=_(""), method=filter_keyword)
	
	class Meta:
		model = Album
		fields = ['title']


class AlbumDetailView(DetailView, View):
	model = Album
	template_name = "photoalbum/album.html"

	def get_context_data(self, **kwargs):
		context = super(AlbumDetailView, self).get_context_data(**kwargs)
	
		album = Album.objects.get(pk=self.kwargs['pk'])
		context['album'] = album
		context['photos'] = album.photos
		context['tags'] = album.tags

		return context


class PhotoDisplay(DetailView):
	model = ResponsiveImage
	template_name = "photoalbum/photo.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoDisplay, self).get_context_data(**kwargs)
		photo = ResponsiveImage.objects.get(pk=self.kwargs['pk'])
		context['photo'] = photo
		#album = context['photo'].get_album()
		#context['album'] = Album.objects.get(pk=album.pk) # TODO: can't I just have album here?
		context['form'] = ReportPhotoForm()
		context['tagged_users'] = context['photo'].get_tagged_users
		#context['next_photo'] = get_next_photo(photo, album)
		#context['previous_photo'] = get_previous_photo(photo, album)
		
		return context


class PhotoReportFormView(SingleObjectMixin, FormView):
	model = ResponsiveImage
	template_name= 'photoalbum/photo.html'
	form_class = ReportPhotoForm

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(PhotoReportFormView, self).post(request, *args, **kwargs)

	def form_invalid(self, form):
		return super().form_invalid(form)

	def form_valid(self, form):
		photo = self.get_object()
		user = self.request.user
		cleaned_data = form.cleaned_data
		report_photo(cleaned_data['reason'], photo, user)

		return super().form_valid(form)
			
	def get_success_url(self):
		photo_pk = self.object.pk
		album_pk = self.object.album.pk
		
		return reverse('photo_detail', kwargs={'pk': self.object.pk, 'album_pk': self.object.album.pk})

	def get_context_data(self, **kwargs):
		context = super(PhotoReportFormView, self).get_context_data(**kwargs)
		context['photo'] = Photo.objects.get(pk=self.kwargs['pk'])
		album = context['photo'].get_album()
		context['album'] = Album.objects.get(pk=album.pk)
		context['form'] = ReportPhotoForm()

		return context


class PhotoDetailView(View):

	def get(self, request, *args, **kwargs):
		view = PhotoDisplay.as_view()
		return view(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		view = PhotoReportFormView.as_view()
		return view(request, *args, **kwargs)



"""
class TagUsersToPhotoFormView(SingleObjectMixin, FormView):
	model = Photo
	tempalte_name = 'photoalbum/photo.html'
	form_class = TagUsersForm

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(TagUsersToPhotoFormView, self).post(request, *args, **kwargs)

	def form_invalid(self, form):
		return super().form_invalid(form)

	def form_valid(self, form):
		photo = self.get_object()
		user = self.request.user
		print("Nickname: ", self.request.user.username)
		cleaned_data = form.cleaned_data
		utils.tag_users(cleaned_data['users'], photo)

		return super().form_valid(form)


	def get_success_url(self):
		photo = self.object
		album = self.object.get_album()

		return reverse('photo_detail', kwargs={'pk': photo.pk, 'album_pk': album.pk, 'album_slug': album.slug })

	def get_context_data(self, **kwargs):
		context = super(TagUsersToPhotoFormView, self).get_context_data(**kwargs)
		context['photo'] = Photo.objects.get(pk=self.kwargs['pk'])
		album = context['photo'].album
		context['album'] = Album.objects.get(pk=album.pk)
		context['form'] = ReportPhotoForm()

		return context
"""
