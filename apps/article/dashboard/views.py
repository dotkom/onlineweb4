# -*- encoding: utf-8 -*-

from collections import Counter
from logging import getLogger

from apps.article.dashboard.forms import ArticleForm
from apps.article.models import Article
from apps.dashboard.tools import check_access_or_403, get_base_context
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from guardian.decorators import permission_required
from taggit.models import TaggedItem


@permission_required('article.view_article')
def article_index(request):
    check_access_or_403(request)

    context = get_base_context(request)
    context['articles'] = Article.objects.all().order_by('-published_date')
    context['years'] = sorted(list(set(a.published_date.year for a in context['articles'])), reverse=True)
    context['pages'] = list(range(1, context['articles'].count() // 10 + 2))

    # Fetch 30 most popular tags from the Django-taggit registry, using a Counter
    queryset = TaggedItem.objects.filter(content_type=ContentType.objects.get_for_model(Article))
    context['tags'] = Counter(map(lambda item: item.tag, queryset)).most_common(30)

    return render(request, 'article/dashboard/article_index.html', context)


@permission_required('article.add_article')
def article_create(request):
    check_access_or_403(request)

    form = ArticleForm()

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.changed_by = request.user
            instance.created_by = request.user
            instance.save()
            form.save_m2m()

            messages.success(request, 'Artikkelen ble opprettet.')
            return redirect(article_detail, article_id=instance.pk)
        else:
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')

    context = get_base_context(request)
    context['form'] = form

    return render(request, 'article/dashboard/article_create.html', context)


@permission_required('article.view_article')
def article_detail(request, article_id):
    check_access_or_403(request)

    article = get_object_or_404(Article, pk=article_id)

    context = get_base_context(request)
    context['article'] = article

    return render(request, 'article/dashboard/article_detail.html', context)


@permission_required('article.change_article')
def article_edit(request, article_id):
    check_access_or_403(request)

    article = get_object_or_404(Article, pk=article_id)

    form = ArticleForm(instance=article)

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'delete':
            instance = get_object_or_404(Article, pk=article_id)
            article_heading = instance.heading
            article_id = instance.id
            instance.delete()
            messages.success(request, '%s ble slettet.' % article_heading)
            getLogger(__name__).info('%s deleted article %d (%s)' % (request.user, article_id, article_heading))

            return redirect(article_index)

        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.changed_by = request.user
            instance.save()
            form.save_m2m()

            messages.success(request, 'Artikkelen ble lagret.')
            getLogger(__name__).info('%s edited article %d (%s)' % (request.user, instance.id, instance.heading))

            return redirect(article_index)
        else:
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')

    context = get_base_context(request)
    context['form'] = form
    context['edit'] = True

    return render(request, 'article/dashboard/article_create.html', context)
