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

    print(request.method)

    if request.method == "POST":
        print("Method is post")
        form = AlbumForm(request.POST, request.FILES)
        print("Request if method is post: ", request)
        if form.is_valid():
            print("Album form is valid")
            form.save()

            return render(request, 'photoalbum/index.html')

    return render(request, 'photoalbum/create.html', {'form': form})
