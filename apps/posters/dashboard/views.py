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
from guardian.models import UserObjectPermission
# from guardian.core import ObjectPermissionChecker
import guardian

from datetime import datetime, timedelta

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import has_access, get_base_context
from apps.posters.models import Poster
from apps.posters.forms import AddPosterForm, EditPosterForm
#from apps.dashboard.posters.models import PosterForm
from apps.companyprofile.models import Company
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

    context = get_base_context(request)

    # View to show if user not in committee, but wanting to see own orders
    if request.user not in group.user_set.all():
        context['your_orders'] = [x for x in Poster.objects.filter(
                                  ordered_by=request.user, display_to__gte=datetime.now())
                                  if request.user.has_perm('view_poster_order', x)]
        return render(request, 'posters/dashboard/index.html', context)

    context['new_orders'] = Poster.objects.filter(assigned_to=None)
    context['active_orders'] = Poster.objects.filter(finished=False).exclude(assigned_to=None)
    context['hanging_orders'] = Poster.objects.filter(finished=True,
                                                      display_to__lte=datetime.now()+timedelta(days=3))
    context['your_orders'] = Poster.objects.filter(assigned_to=request.user,
                                                   finished=False,
                                                   display_to__gte=datetime.now()-timedelta(days=3))


    context['workers'] = User.objects.filter(groups=Group.objects.get(name='proKom'))

    return render(request, 'posters/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request):

    context = get_base_context(request)

    poster = Poster()

    if request.method == 'POST':
        form = AddPosterForm(data=request.POST, instance=poster)
        if form.is_valid():
            poster = form.save(commit=False)
            if request.POST.get('company'):
                poster.company = Company.objects.get(pk=request.POST.get('company'))
            print('ordered by:', request.user)
            poster.ordered_by = request.user
            # Should look for a more kosher solution
            poster.ordered_committee = request.user.groups.filter(name__contains="Kom")[0]

            poster.save()

            # Let this user have permissions to show this order
            UserObjectPermission.objects.assign_perm('view_poster_order', obj=poster, user=request.user)

            return HttpResponseRedirect('../')
        else:
            context['add_poster_form'] = form
            return render(request, 'posters/dashboard/add.html', context)


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
    context['inactive_orders'] = Poster.objects.filter(done=True)[:10]

    today = timezone.now()
    context['active_posters'] = Poster.objects.filter(display_from__lte=today, display_to__gte=today)
    context['inactive_orders'] = Poster.objects.filter(display_to__gte=today)[:5]

    return render(request, 'posters/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('view_poster_order', (Poster, 'pk', 'order_id'), return_403=True)
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

