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
from apps.posters.models import Poster
from apps.posters.forms import AddPosterForm

@ensure_csrf_cookie
@login_required
@permission_required('posters.overview_poster_order', return_403=True)
def index(request):
    if request.is_ajax():
        do_ajax_shit=True

    #posters = Poster.objects.filter()
    context = get_base_context(request)

    return render(request, 'posters/dashboard/overview.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request):
    context = get_base_context(request)
    context['add_poster_form'] = AddPosterForm()
    return render(request, 'posters/dashboard/add.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def change(request):
    context = get_base_context(request)
    context['edit_poster_form'] = EditPosterForm()
    return render(request, 'posters/dashboard/change.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.view_poster_order', return_403=True)
def details(request):
    if request.is_ajax():
        do_ajax_shit=True

    context = get_base_context(request)

    return render(request, 'posters/dashboard/details.html', context)