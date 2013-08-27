from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from models import Article
import django.forms as forms
from django.utils.translation import ugettext_lazy as _
import vimeo
import simplejson as json
import urllib2

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

def completeUpload(request):
    if request.is_ajax:
        client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = True)
        client.token.key = 'ec7d7eb1455e582a97dd732ad74862a9'
        response = json.loads(client.get('vimeo.videos.upload.complete', ticket_id = request.session.get('ticket_id'), filename="wildlife.wmv" ))
        video_data = { 'video_id' : response['ticket']['video_id'] }
        data = json.dumps(video_data)
        print(data)
        return HttpResponse(data, mimetype='application/json')
    else:
        return HttpRequest(status=400)

def vimeoUpload(request):
    client = vimeo.Client(key='c60b0e891d1712b6e86534bcdab319f257a814dd', secret='b2e65f399539d43c9e124afd93476ac95f263b2b', callback='http://127.0.0.1:8000/article/vimeo/', username='user16310918', token = True)
    client.token.key = 'ec7d7eb1455e582a97dd732ad74862a9'
    size_availiable = json.loads(client.get('vimeo.videos.upload.getQuota'))['user']['upload_space']['free']
    request.session['size_availiable'] = size_availiable
    response = json.loads(client.get('vimeo.videos.upload.getTicket'))
    ticket = response['ticket']['endpoint']
    ticket_id = response['ticket']['id']
    request.session['ticket_id'] = ticket_id
    return render_to_response('article/vimeo.html', {'size_availiable' : size_availiable, 'upload_ticket' : ticket, 'ticket_id' : ticket_id  }, context_instance=RequestContext(request))

    
def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
