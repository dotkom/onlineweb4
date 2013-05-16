from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from models import Article
import vimeo

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
    if request.session.get('has_request_token', True) and request.session.get('has_secret_token', True):
        request.session['has_request_token'] = False 
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = False)
        oauth_verif = request.GET.get('oauth_verifier','')
        token = client.exchange_token(oauth_verif)
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = True)
        videos = client.get('vimeo.videos.upload.getQuota')
        print(videos)
        return render_to_response('article/vimeo.html', context_instance=RequestContext(request))

    else:

        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918')
        request.session['has_request_token'] = True
        request.session['has_secret_token'] = True

        return render_to_response('article/vimeo.html', {'authorize_url' : client.authorize_url() }, context_instance=RequestContext(request))

    
def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
