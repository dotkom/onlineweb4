# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from apps.gallery.util import UploadImageHandler
from apps.photoalbum.utils import upload_photos, report_photo, get_or_create_tags, get_tags_as_string
from apps.photoalbum.models import Album, Photo, AlbumTag
from apps.photoalbum.forms import AlbumForm, AlbumForm2, AlbumNameForm, UploadPhotosForm, ReportPhotoForm, AlbumTagsForm


from django_filters import FilterSet, Filter, CharFilter

class AlbumsListView(ListView):
	model = Album
	template_name = 'photoalbum/index.html'
	

	def get(self, request, *args, **kwargs):
		print("In get in albums list view")
		print(request)
		print(*args)
		print(kwargs)
		filter = AlbumFilter(request.GET, queryset=Album.objects.all())
		print("Filtered albums: ", filter)
		#for album in albums:
		#	print("Album in filtered albums: ", album.title)
		#return render(request, 'my_app/template.html', {'filter': filter})


		return render(request, 'photoalbum/index.html', {'filter': filter})

	def get_context_data(self, **kwargs):
		context = super(AlbumsListView, self).get_context_data(**kwargs)
		context['albums'] = Album.objects.all()
		context['filter'] = AlbumFilter(request.GET, queryset=Album.objects.all())
		return context


class AlbumFilter(FilterSet):

	def filter_keyword(self, queryset, value):
		queryset = []
		if value != "":
			list = value.split(" ")

			try:	
				for album in Album.objects.all():
					for word in list:
						print("WOrd: ", word)
						# If word is in title
						if word.lower() in album.title.lower():
							print("Word ", word, " is in album title")
							queryset.append(album)
						else:
							try:
								tag =AlbumTag.objects.get(name=word.lower())
								if tag != None or tag in album.get_tags():
									print("Word ", word, " is tag and album has tag")
									queryset.append(album)
							except Exception:
									print("Tag does not exist")
			except Exception as e:
				print("Exception: ", e)
				queryset = Album.objects.all()
			#else:
				#queryset = Album.objects.filter(Q(title__contains=value) or Q(authors__contains=value))

		else:
			print("Filtering value was empty")
			queryset = Album.objects.all()

		print("Queryset after filtering: ", queryset)

		return queryset


	title = CharFilter(label='Søk', method=filter_keyword)
	class Meta:
		model = Album

		fields = ['title']

def create_album(request):
	if request.method == "POST":
		form = AlbumForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			title = cleaned_data['title']
			album = Album.objects.get_or_create(title=title)[0]
			album.save()

			photos = upload_photos(request.FILES.getlist('photos'), album)
			tags = get_or_create_tags(cleaned_data['tags'], album)
			
			albums = Album.objects.all()
			return render(request, 'photoalbum/index.html', {'albums': albums})
		else:
			print("Form is not valid")

	form = AlbumForm(request.POST)
	return render(request, 'photoalbum/create.html', {'form': form})

#@login_required
def delete_album(request, pk):
	album = Album.objects.get(pk=pk)

	photos = album.get_photos()
	album.delete()

	for photo in photos:
		photo.delete()

	return AlbumsListView.as_view()(request)


class AlbumDetailView(DetailView, View):
	model = Album
	template_name = "photoalbum/album.html"

	print("AlbumDetailView")

	def get_context_data(self, **kwargs):
		context = super(AlbumDetailView, self).get_context_data(**kwargs)
	
		album = Album.objects.get(pk=self.kwargs['pk'])
		context['album'] = album
		context['photos'] = album.get_photos()
		context['tags'] = album.get_tags()

		return context

class PhotoDisplay(DetailView):
	print("PhotoDisplay")
	model = Photo
	template_name = "photoalbum/photo.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoDisplay, self).get_context_data(**kwargs)
		context['photo'] = Photo.objects.get(pk=self.kwargs['pk'])
		album = context['photo'].get_album()
		context['album'] = Album.objects.get(pk=album.pk)
		context['form'] = ReportPhotoForm()

		return context

class PhotoReportFormView(SingleObjectMixin, FormView):
	model = Photo
	template_name= 'photoalbum/photo.html'
	form_class = ReportPhotoForm


	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(PhotoReportFormView, self).post(request, *args, **kwargs)

	def form_invalid(self, form):
		print("Form is invalid")
		print(form.errors)

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
		album = context['photo'].album
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


# Maybe both deletion, editing and creation is supposed to be done from the admin panel?
#@login_required
def edit_album(request, pk):
	album = Album.objects.get(pk=pk)
	photos = album.get_photos()
	name_form = AlbumNameForm(instance=album)
	tags_form = AlbumTagsForm(initial={'tags': get_tags_as_string(album)})
	upload_photos_form = UploadPhotosForm(instance=album)
	
	if request.method == "POST":
		if "edit_name" in request.POST:
			edit_name(request, album)
		elif "edit_tags" in request.POST:
			edit_tags(request, album)
			tags_form = AlbumTagsForm(initial={'tags': get_tags_as_string(album)})
		elif "delete_photos" in request.POST:
			delete_photos(request)
		elif request.FILES.getlist('upload_photos'):
			add_photos(request, album)
			photos = album.get_photos()
		else:
			print("Form is not edit_name, delete_photos or add_photos")

	photos = album.get_photos()
	return render(request, 'photoalbum/edit.html', {'name_form': name_form, 'tags_form': tags_form,'upload_photos_form': upload_photos_form, 'album': album, 'photos': photos})

#@login_required
def edit_name(request, album):
	form = AlbumNameForm(request.POST, request.FILES, instance=album)
	if form.is_valid():
		cleaned_data = form.cleaned_data
		title = cleaned_data['title']
		album.title = title
		album.save()

		#albums = Album.objects.all()
		#return render(request, 'photoalbum/index.html', {'albums': albums})

def edit_tags(request, album):
	form = AlbumTagsForm(request.POST)
	print("In edit_tags")
	if form.is_valid():
		cleaned_data = form.cleaned_data
		print("Edit_tags is valid")

		tags = get_or_create_tags(cleaned_data['tags'], album)
		#album.tags = tags
		#album.save()

		#albums = Album.objects.all()
		#return render(request, 'photoalbum/index.html', {'albums': albums})

#@login_required
def delete_photos(request):	
	photos_to_delete = request.POST.getlist('photos[]')
	if photos_to_delete != []:
		for photo_pk in photos_to_delete:
			photo = Photo.objects.get(pk=photo_pk)
			photo.delete()
	else: 
		print("Photos to delete is empty")

	request_copy = request.POST.copy()
	request_copy = request_copy.setlist('photos[]', [])
	
	#albums = Album.objects.all()
	#return render(request_copy, 'photoalbum/index.html', {'albums': albums})

#@login_required
def add_photos(request, album):
	form = UploadPhotosForm(instance=album)

	photos = upload_photos(request.FILES.getlist('upload_photos'), album)
