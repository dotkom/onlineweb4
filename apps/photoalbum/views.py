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
    

def upload_photos(photos):
    print("PHOTOS")
    print(photos)

    for photo in photos:
        print("Photo")
        print(photo)
        p = Photo()
        p.photo = photo
        p.save()
        print("Created photo")

def create_album(request):
    print("In create_album")
    #log = logging.getLogger(__name__)
   
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)

        print(form)
        print(request.FILES)
        if form.is_valid():
            photos = upload_photos(request.FILES.getlist('photos'))

            album = Album()
            album.title = form['title']
            album.photos = photos
            album.save()
    
            albums = Album.objects.all()
            return render(request, 'photoalbum/index.html', {'albums': albums})
        else:
            print("FOrm is not valid")

    form = AlbumForm(request.POST)
    return render(request, 'photoalbum/create.html', {'form': form})




class AlbumDetailView(DetailView):
    model = Album
    template_name = "photoalbum/album.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
    
        context['album'] = Album.objects.get(pk=self.kwargs['pk'])
        return context



