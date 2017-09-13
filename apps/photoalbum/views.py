from django.shortcuts import render

# Create your views here.

def index(request):

    return render(request, 'photoalbum/index.html')


def test(request):

    return render(request, 'photoalbum/index.html')

