from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from models import Article
from django.utils.translation import ugettext_lazy as _
from apps.article.forms import UploadForm
from apps.article.forms import createUploadForm
import vimeo
import simplejson as json

def index(request):
    # Featured
    featured = Article.objects.filter(featured=True).order_by('-id')[:1]
    
    # Siste 4 nyheter
    latestNews = Article.objects.filter(featured=False).order_by('-id')[:4]
    
    i = 0
    for latest in latestNews:
        if (i % 2 == 0):
            latest.i = 0
        else:
            latest.i = 1
        i += 1
    
    
    return render_to_response('article/index.html', {'featured' : featured[0], 'latest': latestNews}, context_instance=RequestContext(request))

def vimeoUpload(request):
    if request.method == 'POST' and request.session.get('has_authorized', True):
        request.session['has_authorized'] = False
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES['docfile'].size > request.session.get('size_availiable'):
                messages.error(request, _(u'Filen var for stor'))
            else:
                client = request.session['client']
                ticket = json.loads(client.get('vimeo.videos.upload.getTicket', upload_method='streaming'))
                print(ticket)
                
        else:
            messages.error(request, _(u'Det oppstod en feil.'))
        return render_to_response('article/vimeo.html', {'message' : "upload is good"}, context_instance=RequestContext(request))
    elif request.session.get('has_authorized', True):
        oauth_verif = request.GET.get('oauth_verifier', '')
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = False)
        token = client.exchange_token(oauth_verif)
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = True)
        request.session['client'] = client
        size_availiable = json.loads(client.get('vimeo.videos.upload.getQuota'))['user']['upload_space']['free']
        request.session['size_availiable'] = size_availiable
        form = createUploadForm(size_availiable)
        return render_to_response('article/vimeo.html', {'form' : form, 'size_availiable' : size_availiable }, context_instance=RequestContext(request))
    else:
        print("start")
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918')
        request.session['has_authorized'] = True
        return render_to_response('article/vimeo.html', {'authorize_url' : client.authorize_url(permission='write') }, context_instance=RequestContext(request))

    
def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
