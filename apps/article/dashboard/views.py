# -*- encoding: utf-8 -*-
from django.shortcuts import render, get_object_or_404

from guardian.decorators import permission_required

from apps.dashboard.tools import check_access_or_403, get_base_context


def article_index(request):
    yield()


def article_create(request, article_id):
    yield()


def article_change(request, article_id, article_slug):
    yield()


@permission_required('article.view_tag')
def tag_index(request):
    check_access_or_403()

    context = get_base_context(request)
    context['articles'] = Article.objects.all()

    return render(request, 'article/dashboard/index.html', context)


@permission_required('article.tag_create')
def tag_create(request):
    yield()


@permission_required('article.change')
def tag_change(request, name, slug):
    yield()
