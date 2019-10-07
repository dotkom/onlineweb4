from django.shortcuts import render

from apps.photoalbum.models import Album, Photo
from apps.photoalbum.forms import AlbumForm


def index(request):

    albums = Album.objects.all()
    return render(request, 'photoalbum/index.html')


def album(request):

    photos = Photo.all()

    return render(request, 'photoalbum/{% album.title %}')


def create_album(request):
    form = AlbumForm(request.POST)
    print("In create")

    if request.method == "post":
        print("Method is post")
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            print("Album form is valid")

            return render(request, 'photoalbum/index.html', {'form': form})

    return render(request, 'photoalbum/create.html', {'form': form})
