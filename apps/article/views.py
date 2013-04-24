from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from models import Article, Tag, ArticleTag
import random

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
        Article month (published_date), most likely in norwegian written format.
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

    rev_month_strings = dict((v,k) for k,v in month_strings.iteritems())

    # For creating the date filters.
    dates = {}
    for article in articles:
        d_year = str(article.published_date.year)
        d_month = str(article.published_date.month)
        if d_year not in dates:
            dates[d_year] = []
        for y in dates:
            if d_year == y:
                if month_strings[d_month] not in dates[d_year]:
                    dates[d_year].append(month_strings[d_month])

    # If we're filtering by tag
    if name:
        filtered = []
        for article in articles:
            for tag in article.tags:
                if name == tag.name:
                    filtered.append(article)
        articles = filtered

    # If we're filtering by year
    if 'year' in request.path:
        filtered = []
        # If we're filtering by year and month
        if 'month' in request.path:
            month = rev_month_strings[month]
            for article in articles:
                if article.published_date.year == int(year) and article.published_date.month == int(month):
                    filtered.append(article)
        # If we're filtering by year, but not month
        else:
            for article in articles:
                if article.published_date.year == int(year):
                    filtered.append(article)
        articles = filtered

    # Get the 30 most used tags, then randomize them
    tags = list(Tag.objects.all())
    tags.sort(key=lambda x: x.frequency, reverse=True)
    tags = tags[:30]
    random.shuffle(tags)
    # Get max frequency of tags. This is used for relative sizing in the tag cloud.
    max_tag_frequency = max([x.frequency for x in tags])

    return render_to_response('article/archive.html', {'articles': articles, 'tags': tags, 'max_tag_frequency': max_tag_frequency, 'dates': dates } ,context_instance=RequestContext(request))

def archive_tag(request, name, slug):
    return archive(request, name=name, slug=slug)

def archive_year(request, year):
    return archive(request, year=year)

def archive_month(request, year, month):
    return archive(request, year=year, month=month)

def details(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	
	if (article.changed_date != article.created_date):
		article.isChanged = True
	else:
		article.isChanged = False
		
	return render_to_response('article/details.html', {'article': article}, context_instance=RequestContext(request))
