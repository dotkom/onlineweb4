from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.db.models import Count
from models import Article, Tag, ArticleTag
import random
import simplejson as json
import vimeo

oauth_key = 'c60b0e891d1712b6e86534bcdab319f257a814dd' 
oauth_secret = 'b2e65f399539d43c9e124afd93476ac95f263b2b'
oauth_token = 'ec7d7eb1455e582a97dd732ad74862a9'
vimeo_username = 'user16310918'

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
        return HttpResponse(data, mimetype='application/json')
    else:
        return HttpRequest(status=400)

def vimeoUpload(request):
    client = vimeo.Client(key=oauth_key, secret=oauth_secret, callback='http://127.0.0.1:8000/article/vimeo_upload/', username=vimeo_username, token = True)
    client.token.key = oauth_token
    size_availiable = json.loads(client.get('vimeo.videos.upload.getQuota'))['user']['upload_space']['free']
    request.session['size_availiable'] = size_availiable
    response = json.loads(client.get('vimeo.videos.upload.getTicket'))
    ticket = response['ticket']['endpoint']
    ticket_id = response['ticket']['id']
    request.session['ticket_id'] = ticket_id
    return render_to_response('article/vimeo_upload.html', {'size_availiable' : size_availiable, 'upload_ticket' : ticket, 'ticket_id' : ticket_id  }, context_instance=RequestContext(request))

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

    articles = Article.objects.all().order_by('-published_date')

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
    try:
        max_tag_frequency = max([x.frequency for x in tags])
    except ValueError:
        max_tag_frequency = 1

    # Paginator
    # Shows 10 articles per page. Note that these are also filtered beforehand by tag or date.
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # Deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # Deliver last page.
        articles = paginator.page(paginator.num_pages)

    return render_to_response('article/archive.html', {'articles': articles, 'tags': tags, 'max_tag_frequency': max_tag_frequency, 'dates': dates } ,context_instance=RequestContext(request))

def archive_tag(request, name, slug):
    return archive(request, name=name, slug=slug)

def archive_year(request, year):
    return archive(request, year=year)

def archive_month(request, year, month):
    return archive(request, year=year, month=month)

def details(request, article_id):

    article = get_object_or_404(Article, pk=article_id)

    if article.changed_date != article.created_date:
        article.is_changed = True
    else:
        article.is_changed = False

    related_articles = Article.objects.filter(article_tags__tag__in=article.tags).distinct().annotate(num_tags=Count('article_tags__tag')).order_by('-num_tags', '-published_date').exclude(id=article.id)[:4]

    return render_to_response('article/details.html', {'article': article, 'related_articles': related_articles}, context_instance=RequestContext(request))
