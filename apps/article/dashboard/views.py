# -*- encoding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from guardian.decorators import permission_required

from apps.article.models import Article, Tag
from apps.article.dashboard.forms import TagForm, ArticleForm
from apps.dashboard.tools import check_access_or_403, get_base_context


@permission_required('article.view_article')
def article_index(request):
    check_access_or_403(request)

    context = get_base_context(request)
    context['articles'] = Article.objects.all()
    context['years'] = sorted(list(set(a.published_date.year for a in context['articles'])), reverse=True)

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
            messages.success(request, u'Artikkelen ble opprettet.')
            redirect(article_detail(instance.pk))
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')

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
        form = ArticleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.changed_by = request.user
            instance.save()
            messages.success(request, u'Artikkelen ble lagret.')
            redirect(article_index)
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')

    context = get_base_context(request)
    context['form'] = form
    context['edit'] = True
    
    return render(request, 'article/dashboard/article_create.html', context)


@permission_required('article.view_tag')
def tag_index(request):
    check_access_or_403(request)

    context = get_base_context(request)
    context['tags'] = Tag.objects.all()

    return render(request, 'article/dashboard/tag_index.html', context)


@permission_required('article.add_tag')
def tag_create(request):
    check_access_or_403(request)

    form = TagForm()

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'Tag ble opprettet.')
            redirect(tag_index)
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')

    context = get_base_context(request)
    context['form'] = form

    return render(request, 'article/dashboard/tag_create.html', context)


@permission_required('article.change_tag')
def tag_edit(request, tag_id):
    check_access_or_403(request)

    tag = get_object_or_404(Tag, pk=tag_id)

    form = TagForm(instance=tag)

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'Tag ble opprettet.')
            redirect(tag_index)
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')

    context = get_base_context(request)
    context['form'] = form
    context['edit'] = True
    
    return render(request, 'article/dashboard/tag_create.html', context)
