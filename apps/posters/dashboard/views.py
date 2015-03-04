# -*- encoding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.dashboard.posters.models import PosterForm


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request):
    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)
    if request.is_ajax():
        do_ajax_shit=True

    if request.method == 'GET':
            posterform = PosterForm()

    else:
        # A POST request: Handle Form Upload
        form = PostForm(request.POST) # Bind data from request.POST into a PostForm
 
        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            shit=True
            #content = form.cleaned_data['content']
            #created_at = form.cleaned_data['created_at']
            #post = m.Post.objects.create(content=content,
            #                             created_at=created_at)
            #return HttpResponseRedirect(reverse('post_detail',
            #                                    kwargs={'post_id': post.id}))

    return render(request, 'posters/dashboard/add.html', {'PosterForm': posterform, context})



@ensure_csrf_cookie
@login_required
@permission_required('posters.overview_poster_order', return_403=True)
def index(request):
    if request.is_ajax():
        do_ajax_shit=True

    context = get_base_context(request)

    return render(request, 'posters/dashboard/view.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.view_poster_order', return_403=True)
def details(request):
    if request.is_ajax():
        do_ajax_shit=True

    context = get_base_context(request)

    return render(request, 'posters/dashboard/overview.html', context)