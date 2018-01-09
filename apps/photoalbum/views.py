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


# Gives NonType Error when used
class CreateAlbum(FormView):
    print("In CreateAlbumView")
    
    form_class = AlbumForm
    template_name = '/photoalbum/create.html' # Replace with your template.
    success_url = '/photoalbum/index.html'  # Replace with your URL or reverse().


    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        photos = request.FILES.getlist('photos')
        if form.is_valid():
            for photo in photos:

                console.log("Photo!")
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    



def upload_photos(photos, album):
    photos_list = []


    for photo in photos:
        print("photo: ", photo)
        p = Photo(photo=photo, album=album)
        print(p)
        p.save()
        photos_list.append(p)
        print("Created photo")

    print("Photos list")
    print(photos_list)
    return photos_list




def upload_photo(photo):
    photos_list = []



    print("photo: ", photo[0])
    p = Photo(photo=photo[0])
    print(p)
    p.save()
    photos_list.append(p)
    print("Created photo")

    print("Photos list")
    print(photos_list)
    return photos_list

def create_album(request):
    print("In create_album")
    #log = logging.getLogger(__name__)
   
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            album = Album()
            album.title = cleaned_data['title']
            album.save()

            photos = upload_photos(request.FILES.getlist('photos'), album)
            
    
            albums = Album.objects.all()

            return render(request, 'photoalbum/index.html', {'albums': albums})
        else:
            print("Form is not valid")

    form = AlbumForm(request.POST)
    return render(request, 'photoalbum/create.html', {'form': form})




class AlbumDetailView(DetailView):
    model = Album
    template_name = "photoalbum/album.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
    
        context['album'] = Album.objects.get(pk=self.kwargs['pk'])
        context['photos'] = Photo.objects.all().filter(album=context['album'])
        print(context['photos'])
        return context



