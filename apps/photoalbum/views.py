from django.shortcuts import render

from apps.photoalbum.models import Album, Photo
from apps.photoalbum.forms import AlbumForm, AlbumForm2, AlbumNameForm, UploadPhotosForm

from django.shortcuts import render, HttpResponseRedirect

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from apps.gallery.util import UploadImageHandler
from utils import upload_photos


class AlbumsListView(ListView):
	model = Album
	template_name = 'photoalbum/index.html'

	def get_context_data(self, **kwargs):
		context = super(AlbumsListView, self).get_context_data(**kwargs)
		context['albums'] = Album.objects.all()
		return context

@login_required
def create_album(request):
	if request.method == "POST":
		form = AlbumForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			title = cleaned_data['title']
			album = Album.objects.get_or_create(title=title)[0]
			album.save()

			photos = upload_photos(request.FILES.getlist('photos'), album)
			
			albums = Album.objects.all()
			return render(request, 'photoalbum/index.html', {'albums': albums})

			return AlbumsListView.as_view()(request)
		else:
			print("Form is not valid")

	form = AlbumForm(request.POST)
	return render(request, 'photoalbum/create.html', {'form': form})

@login_required
def delete_album(request, pk):
	album = Album.objects.filter(pk=pk)

	photos = Photo.objects.all().filter(album=album)
	album.delete()

	for photo in photos:
		photo.delete()

	return AlbumsListView.as_view()(request)


class AlbumDetailView(DetailView):
	model = Album
	template_name = "photoalbum/album.html"

	def get_context_data(self, **kwargs):
		context = super(AlbumDetailView, self).get_context_data(**kwargs)
	
		context['album'] = Album.objects.get(pk=self.kwargs['pk'])
		context['photos'] = Photo.objects.all().filter(album=context['album'])

		return context

class PhotoDetailView(DetailView):
	model = Photo
	template_name = "photoalbum/photo.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoDetailView, self).get_context_data(**kwargs)
		context['photo'] = Photo.objects.get(pk=self.kwargs['pk'])
		album = context['photo'].album
		context['album'] = Album.objects.get(pk=album.pk)

		return context

# Maybe both deletion, editing and creation is supposed to be done from the admin panel?
@login_required
def edit_album(request, pk):
	album = Album.objects.get(pk=pk)
	photos = Photo.objects.all().filter(album=album)
	name_form = AlbumNameForm(instance=album)
	upload_photos_form = UploadPhotosForm(instance=album)
	
	if request.method == "POST":
		if "edit_name" in request.POST:
			edit_name(request, album)
		elif "delete_photos" in request.POST:
 			delete_photos(request)
		elif request.FILES.getlist('upload_photos'):
			add_photos(request, album)
			photos = Photo.objects.all().filter(album=album)
		else:
			print("Form is not edit_name, delete_photos or add_photos")

	photos = Photo.objects.all().filter(album=album)
	return render(request, 'photoalbum/edit.html', {'name_form': name_form, 'upload_photos_form': upload_photos_form, 'album': album, 'photos': photos})

@login_required
def edit_name(request, album):
	form = AlbumNameForm(request.POST, request.FILES, instance=album)
	if form.is_valid():
		cleaned_data = form.cleaned_data
		title = cleaned_data['title']
		album.title = title
		album.save()
		
		albums = Album.objects.all()
		return render(request, 'photoalbum/index.html', {'albums': albums})

@login_required
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
	albums = Album.objects.all()
	return render(request_copy, 'photoalbum/index.html', {'albums': albums})

@login_required
def add_photos(request, album):
	form = UploadPhotosForm(instance=album)

	photos = upload_photos(request.FILES.getlist('upload_photos'), album)
