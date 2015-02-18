# -*- encoding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from guardian.decorators import permission_required

from apps.article.models import Article, Tag
from apps.article.dashboard.forms import TagForm, ArticleForm
from apps.dashboard.tools import check_access_or_403, get_base_context


def article_index(request):
    yield()


def article_create(request, article_id):
    yield()


def article_change(request, article_id):
    yield()


@permission_required('article.view_tag')
def tag_index(request):
    check_access_or_403(request)

    context = get_base_context(request)
    context['tags'] = Tag.objects.all()

    return render(request, 'article/dashboard/tag_index.html', context)


@permission_required('article.tag_create')
def tag_create(request):
    check_access_or_403(request)

    form = TagForm()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.sucess(request, u'Tag ble opprettet.')
            redirect('dashboard_tag_index')
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
            form = TagForm(request.POST)

    context = get_base_context(request)
    context['form'] = form

    return render(request, 'article/dashboard/tag_create.html', context)


@permission_required('article.change')
def tag_change(request, tag_id):
    check_access_or_403(request)

    tag = get_object_or_404(Tag, pk=tag_id)

    form = TagForm(instance=tag)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.sucess(request, u'Tag ble opprettet.')
            redirect('dashboard_tag_index')
        else:
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
            form = TagForm(request.POST)

    context = get_base_context(request)
    context['form'] = form
    
    return render(request, 'article/dashboard/tag_create.html', context)
