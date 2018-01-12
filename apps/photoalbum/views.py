from django.shortcuts import render

from apps.photoalbum.models import Album, Photo
from apps.photoalbum.forms import AlbumForm

from django.shortcuts import render, HttpResponseRedirect

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from apps.gallery.util import UploadImageHandler

from apps.photoalbum.forms import AlbumForm2

class AlbumsListView(ListView):
    model = Album
    template_name = 'photoalbum/index.html'

    def get_context_data(self, **kwargs):
        context = super(AlbumsListView, self).get_context_data(**kwargs)
        context['albums'] = Album.objects.all()
        print("Albums: ")
        print(context['albums'])
        for album in context['albums']:
            print("Album: ", album.title)
        return context


def upload_photos(photos, album):
    photos_list = []

    for photo in photos:
        p = Photo(photo=photo, album=album)
        p.save()
        photos_list.append(p)

    return photos_list

def create_album(request):
    print("In create_album")
    #log = logging.getLogger(__name__)
   
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
        else:
            print("Form is not valid")

    form = AlbumForm(request.POST)
    return render(request, 'photoalbum/create.html', {'form': form})

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
        print("Before getting album pk")
        album = context['photo'].album
        print("Album pk: ", album.pk)
        context['album'] = Album.objects.get(pk=album.pk)
        return context

