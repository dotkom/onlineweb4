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


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request):
    if request.is_ajax():
        do_ajax_shit=True

    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    #context['poster_orders'] = 1
    
    return render(request, 'posters/dashboard/add.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.view_poster_order', return_403=True)
def overview(request):
    if request.is_ajax():
        do_ajax_shit=True

    return render(request, 'posters/dashboard/view.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.overview_poster_order', return_403=True)
def overview(request):
    if request.is_ajax():
        do_ajax_shit=True

    return render(request, 'posters/dashboard/overview.html', context)