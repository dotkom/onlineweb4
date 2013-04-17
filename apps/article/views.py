from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from models import Article, Tag

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

def archive(request, name=None, slug=None, year=None, month=None):
    """
    Parameters
    ----------
    name:
        Tag name
    slug:
        Tag slug
    year:
        Article year (published_date)
    month:
        Article month (published_date)
    """

    articles = Article.objects.all()

    month_strings = {
        '1': u'Januar',
        '2': u'Februar',
        '3': u'Mars',
        '4': u'April',
        '5': u'Mai',
        '6': u'Juni',
        '7': u'Juli',
        '8': u'August',
        '9': u'September',
        '10': u'Oktober',
        '11': u'November',
        '12': u'Desember',
    }

    dates = {}
    for article in articles:
        year = str(article.published_date.year)
        month = str(article.published_date.month)
        if year not in dates:
            dates[year] = []
        for y in dates:
            if year == y:
                if month_strings[month] not in dates[year]:
                    dates[year].append(month_strings[month])

    if name:
        filtered = []
        for article in articles:
            for tag in article.tags:
                if name == tag.name:
                    filtered.append(article)
        articles = filtered

    tags = Tag.objects.all().order_by('?')

    return render_to_response('article/archive.html', {'articles': articles, 'tags': tags, 'dates': dates } ,context_instance=RequestContext(request))

def archive_tag(request, name, slug):
    return archive(request, name=name, slug=slug)

def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
