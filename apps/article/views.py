from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from models import Article

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

def archive(request):
    return render_to_response('article/archive.html', context_instance=RequestContext(request))

def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
