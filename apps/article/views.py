from collections import Counter

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from taggit.models import TaggedItem

from apps.article.filters import ArticlesFilter
from apps.article.models import Article
from apps.article.serializers import ArticleSerializer
from apps.article.utils import create_article_filters


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

    articles = Article.objects.filter(published_date__lte=timezone.now()).order_by(
        "-published_date"
    )

    dates = create_article_filters(articles)

    # Fetch 30 most popular tags from the Django-taggit registry, using a Counter
    queryset = TaggedItem.objects.filter(
        content_type=ContentType.objects.get_for_model(Article)
    )
    if name and slug:
        queryset = queryset.filter(tag__name=name)
    tags = Counter(item.tag for item in queryset).most_common(30)

    return render(request, "article/archive.html", {"tags": tags, "dates": dates})


def archive_tag(request, slug):
    return archive(request, slug=slug)


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

    related_articles = (
        Article.objects.exclude(pk=article_id)
        .filter(tags__in=article.tags.all())
        .distinct()[:4]
    )

    return render(
        request,
        "article/details.html",
        {"article": article, "related_articles": related_articles},
    )


# API v1 Views


class ArticleViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    """
    Article viewset. Can be filtered on 'year', 'month', 'tags' and free text search using 'query'.

    Filtering on tags is only supported if the tags are supplied exactly as the stored tags.
    """

    queryset = Article.objects.filter()
    serializer_class = ArticleSerializer
    permission_classes = (AllowAny,)
    filterset_class = ArticlesFilter
    ordering_fields = ["id", "changed_date", "published_date", "created_date"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(published_date__lte=timezone.now())
            .order_by("-published_date")
        )
