# -*- coding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, viewsets
from watson import search as watson

from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView



from django import forms


from apps.gallery.util import UploadImageHandler
from apps.gallery.models import ResponsiveImage

from apps.photoalbum.utils import report_photo, get_tags_as_string, get_previous_photo, get_next_photo, is_prokom, clear_tags_to_album
from apps.photoalbum.models import Album
from apps.photoalbum.forms import ReportPhotoForm
#from django_filters import FilterSet, Filter, CharFilter
from apps.photoalbum.decorators import prokom_required
from apps.photoalbum import utils

class AlbumsListView(ListView):
	model = Album
	template_name = 'photoalbum/index.html'

	def get_context_data(self, **kwargs):
		context = super(AlbumsListView, self).get_context_data(**kwargs)

		context['albums'] = Album.objects.all()
		print(context['albums'][0])
		return context

"""
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
"""

class AlbumDetailView(DetailView, View):
	print("In album detail view")
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
		album = Album.objects.get(pk=self.kwargs['album_pk'])
		
		context['photo'] = photo
		context['album'] = album
		context['form'] = ReportPhotoForm()
		context['tagged_users'] = context['photo'].tags
		context['next_photo'] = get_next_photo(photo, album)
		context['previous_photo'] = get_previous_photo(photo, album)
		
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
class PhotoAlbumViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):

	queryset = Album.objects.all().order_by('-timestamp')[:15]

	def get_queryset(self):
			queryset = Album.objects.all().order_by('-timestamp')[:15]
			year = self.request.query_params.get('year', None)
			tags = self.request.query_params.get('tags', None)
			query= self.request.query_params.get('query', None)

			if tags:
				queryset = queryset.filter(Q(tags__name__in=[tags]) | Q(tags__slug__in=[tags]))
			if year:
				queryset = queryset.filter(
					published_data__year=year,
					published_date__lte=timezone.now()  
				).order_by('-published_date')

			if query and query != '':
				queryset = watson.filter(queryset, query)

			return queryset
"""





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
