from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    """
    A simple hello world in django 1.4.
    I have never seen this idiom before, but I like it! -Sigurd
    """
    t = loader.get_template('events/index.html')
    c = Context({
        'message': 'hello world! =)',
        })
    return HttpResponse(t.render(c))
