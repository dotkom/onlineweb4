from django.shortcuts import render

from apps.photoalbum.models import Album, Photo
from apps.photoalbum.forms import AlbumForm

from django.shortcuts import render, HttpResponseRedirect

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from apps.gallery.util import UploadImageHandler

from apps.photoalbum.forms import AlbumForm

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
    


def create_album(request):
    print("In create_album")
    #log = logging.getLogger(__name__)
    form = AlbumForm(request.POST)
    print(form)
    
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            images = upload(request)
            album = form.save()
            album.save()
    
            albums = Album.objects.all()
            return render(request, 'photoalbum/index.html', {'albums': albums})

    return render(request, 'photoalbum/create.html', {'form': form})


def upload(request):

    images = UploadImageHandler(request.FILES['images']).status
    if not result: 
        return JsonResponse({'success': False, 'message': result.message}, status=500)

        # Return OK if all is good
        return JsonResponse({'success': True, 'message': 'OK'}, status=200)
    return JsonResponse({'success': False, 'message': 'Bad request or invalid type'}, status=400)


class AlbumDetailView(DetailView):
    model = Album
    template_name = "photoalbum/album.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
    
        context['album'] = Album.objects.get(pk=self.kwargs['pk'])
        return context



