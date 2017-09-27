from django.shortcuts import render

from apps.photoalbum.models import Album, Photo
from apps.photoalbum.forms import AlbumForm

from django.shortcuts import render, HttpResponseRedirect

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator


class AlbumsListView(ListView):
    model = Album
    template_name = 'photoalbum/index.html'

    def get_context_data(self, **kwargs):
        context = super(AlbumsListView, self).get_context_data(**kwargs)
        context['albums'] = Album.objects.all()
        return context


def create_album(request):
    form = AlbumForm(request.POST)
    print("In create")

    print(request.method)

    if request.method == "POST":
        print("Method is post")
        form = AlbumForm(request.POST, request.FILES)
        print("Request if method is post: ", request)
        if form.is_valid():
            print("Album form is valid")
            print("Form: ", form)

            album = form.save()
            print("Album: ", album.title)
            album.save()
            print("Albums after save: ", Album.objects.all())

            albums = Album.objects.all()
            return render(request, 'photoalbum/index.html', {'albums': albums})

    return render(request, 'photoalbum/create.html', {'form': form})


class AlbumDetailView(DetailView):
    model = Album
    template_name = "photoalbum/album.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        context['album'] = Album.objects.get(pk=self.kwargs['pk'])
        return context



