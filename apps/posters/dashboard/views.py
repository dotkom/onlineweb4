# -*- encoding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.posters.models import Poster
from apps.posters.forms import AddPosterForm, EditPosterForm
#from apps.dashboard.posters.models import PosterForm
from apps.posters.models import Poster


@ensure_csrf_cookie
@login_required
@permission_required('posters.overview_poster_order', return_403=True)
def index(request):
    if request.is_ajax():
        do_ajax_shit=True

    #posters = Poster.objects.filter()
    context = get_base_context(request)

    return render(request, 'posters/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request):
    if request.method == 'POST':
        form = AddPosterForm(data=request.POST)
        if form.is_valid():
            poster=Poster(request.POST)
            #poster.ordered_by = request.user
            #poster.ordered_committee = request.user.groups.filter(name="dotKom")[:1].get();
            poster.save()

            return HttpResponseRedirect('../')
        else:
            print("invalid form")
#    if request.method == 'GET':
#            posterform = PosterForm()

#    else:
        # A POST request: Handle Form Upload
        #form = PostForm(request.POST) # Bind data from request.POST into a PostForm
 
        # If data is valid, proceeds to create a new post and redirect the user
        #if form.is_valid():
     #       shit=True
            #content = form.cleaned_data['content']
            #created_at = form.cleaned_data['created_at']
            #post = m.Post.objects.create(content=content,
            #                             created_at=created_at)
            #return HttpResponseRedirect(reverse('post_detail',
            #                                    kwargs={'post_id': post.id}))

    #return render(request, 'posters/dashboard/add.html', {'PosterForm': posterform, context})

    context = get_base_context(request)
    context['add_poster_form'] = AddPosterForm()
    return render(request, 'posters/dashboard/add.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def change(request):
    context = get_base_context(request)
    context['edit_poster_form'] = EditPosterForm()
    context['new_orders'] = Poster.objects.filter(assigned_to=None)
    context['active_orders'] = Poster.objects.filter(done=False, assigned_to__isnull=False)
    context['inactive_orders'] = Poster.objects.filter(done=True).order_by('-id')[:10]

    today = timezone.now()
    context['active_posters'] = Poster.objects.filter(display_from__lte=today, display_to__gte=today)
    context['inactive_orders'] = Poster.objects.filter(display_to__gte=today)[:5]

    return render(request, 'posters/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.view_poster_order', return_403=True)
def details(request):
    if request.is_ajax():
        do_ajax_shit=True

    context = get_base_context(request)

    return render(request, 'posters/dashboard/details.html', context)
