# -*- encoding: utf-8 -*-
from django.shortcuts import render, get_object_or_404

from guardian.decorators import permission_required

from apps.article.models import Article, Tag
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
    yield()


@permission_required('article.change')
def tag_change(request, tag_id):
    yield()
