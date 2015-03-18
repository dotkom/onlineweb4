# -*- encoding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from guardian.decorators import permission_required

from apps.authentication.models import OnlineUser as User
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

    # The group with members who should populate the dropdownlist
    group = Group.objects.get(name='proKom')
    users_to_populate = group.user_set.all()
    print(users_to_populate)


    context = get_base_context(request)
    context['new_orders'] = Poster.objects.filter(assigned_to=None).order_by('-id')
    context['active_orders'] = Poster.objects.filter(finished=False).order_by('-id')
    context['workers'] = User.objects.filter(groups=Group.objects.get(name='proKom'))

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
def detail(request, order_id=None):
    if request.is_ajax():
        do_ajax_shit=True

    context = get_base_context(request)

    return render(request, 'posters/dashboard/details.html', context)


# Ajax


# @ensure_csrf_cookie
@login_required
@permission_required('posters.view_poster_order', return_403=True)
def assign_person(request):
    if request.is_ajax():
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            orders = Poster.objects.filter(pk=order_id)
            assign_to_id = request.POST.get('assign_to_id')
            assign_to = User.objects.get(pk=assign_to_id)

            if orders.count() == 0:
                response_text = json.dumps({'message': _(
                    u"""Kan ikke finne en ordre med denne IDen (%s).
Om feilen vedvarer etter en refresh, kontakt dotkom@online.ntnu.no.""") % order_id})
                return HttpResponse(status=412, content=response_text)

            order = orders[0]

            if order.finished or order.assigned_to is not None:
                response_text = json.dumps({'message': _(u"Denne ordren er allerede behandlet.")})
                return HttpResponse(status=412, content=response_text)

            order.assigned_to = assign_to
            order.save()

            return HttpResponse(status=200)

