import random

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, Context, loader, RequestContext

from apps.article.models import Article, Tag, ArticleTag


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

    articles = Article.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

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

    # HERE BE DRAGONS
    # TODO: Fix all these for loops...
    # --------------------------------
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
    # Now sort months
    for year in dates:
        sorted_months = ['' for x in range(1, 13)]
        for month in dates[year]:
            sorted_months[int(rev_month_strings[month])-1] = month
        remove_these = []
        for n, m in enumerate(sorted_months):
            if m == '':
                remove_these.append(n)
        for i in reversed(remove_these):
            del sorted_months[i]
        dates[year] = sorted_months

    # Get the 30 most used tags, then randomize them
    tags = Tag.objects.filter(article_tags__isnull=False).distinct().annotate(num_tags=Count('article_tags__tag')).order_by('-num_tags')
    tags = list(tags[:30])
    random.shuffle(tags)

    return render_to_response('article/archive.html', {'tags': tags, 'dates': dates } ,context_instance=RequestContext(request))

def archive_tag(request, name, slug):
    return archive(request, name=name, slug=slug)

def archive_year(request, year):
    return archive(request, year=year)

def archive_month(request, year, month):
    return archive(request, year=year, month=month)

def details(request, article_id, article_slug):

    article = get_object_or_404(Article, pk=article_id)

    if article.changed_date != article.created_date:
        article.is_changed = True
    else:
        article.is_changed = False

    if len(article.additional_authors) != 0:
        article.multiple_authors = True
    else:
        article.multiple_authors = False

    if len(article.photographers) != 0:
        article.multiple_photographers = True
    else:
        article.multiple_photographers = False


    related_articles = Article.objects.filter(article_tags__tag__in=article.tags).distinct().annotate(num_tags=Count('article_tags__tag')).order_by('-num_tags', '-published_date').exclude(id=article.id)[:4]

    return render_to_response('article/details.html', {'article': article, 'related_articles': related_articles}, context_instance=RequestContext(request))
