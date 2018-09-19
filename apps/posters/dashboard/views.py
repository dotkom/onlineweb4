# -*- encoding: utf-8 -*-

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.mail import EmailMessage
from django.shortcuts import HttpResponse, HttpResponseRedirect, get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from guardian.decorators import permission_required
from guardian.models import GroupObjectPermission, UserObjectPermission

from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company
from apps.dashboard.tools import get_base_context
from apps.posters.forms import (AddBongForm, AddOtherForm, AddPosterForm, EditOtherForm,
                                EditPosterForm)
from apps.posters.models import Poster
from apps.posters.permissions import has_edit_perms, has_view_all_perms, has_view_perms


@login_required
@permission_required('posters.overview_poster_order', return_403=True)
def index(request):

    # The group with members who should populate the dropdownlist
    group = Group.objects.get(name='proKom')
    users_to_populate = group.user_set.all()

    context = get_base_context(request)

    # View to show if user not in committee, but wanting to see own orders
    if not has_view_all_perms(request.user):
        context['your_orders'] = [x for x in Poster.objects.filter(ordered_by=request.user)
                                  if request.user.has_perm('view_poster_order', x)]
        return render(request, 'posters/dashboard/index.html', context)

    orders = Poster.objects.all()

    context['new_orders'] = orders.filter(assigned_to=None)
    context['active_orders'] = orders.filter(finished=False).exclude(assigned_to=None)
    context['old_orders'] = orders.filter(finished=True)

    context['workers'] = users_to_populate

    return render(request, 'posters/dashboard/index.html', context)


@login_required
@permission_required('posters.add_poster_order', return_403=True)
def add(request, order_type=0):
    order_type = int(order_type)
    context = get_base_context(request)
    type_names = ("Plakat", "Bong", "Generell ")
    type_name = type_names[order_type-1]

    poster = Poster()
    form = None

    if request.method == 'POST':
        if order_type == 1:
            form = AddPosterForm(data=request.POST, instance=poster)
        elif order_type == 2:
            form = AddBongForm(data=request.POST, instance=poster)
        elif order_type == 3:
            # poster = GeneralOrder()
            form = AddOtherForm(data=request.POST, instance=poster)

        if form.is_valid():
            _handle_poster_add(request, form, order_type)
            return redirect(poster.get_absolute_url())
        else:
            context['form'] = form
            context['form'].fields['ordered_committee'].queryset = request.user.groups.all()
            return render(request, 'posters/dashboard/add.html', context)

    context["order_type_name"] = type_name
    context['order_type'] = order_type
    context['can_edit'] = request.user.has_perm('posters.view_poster')

    if order_type == 1:
        AddPosterForm()
    elif order_type == 2:
        AddBongForm()
    elif order_type == 3:
        AddOtherForm()

    forms = (AddPosterForm(), AddBongForm(), AddOtherForm())

    context['form'] = forms[order_type-1]
    context['form'].fields['ordered_committee'].queryset = request.user.groups.all()

    return render(request, 'posters/dashboard/add.html', context)


@ensure_csrf_cookie
@login_required
def edit(request, order_id=None):
    context = get_base_context(request)
    context['add_poster_form'] = AddPosterForm()

    if order_id:
        poster = get_object_or_404(Poster, pk=order_id)
    else:
        poster = order_id

    if order_id and request.user != poster.ordered_by and 'proKom' not in request.user.groups.all():
        raise PermissionDenied

    selected_form = EditPosterForm

    if request.POST:
        if poster.title:
            selected_form = EditOtherForm
        form = selected_form(request.POST, instance=poster)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("../detail/"+str(poster.id))
        else:
            context["form"] = form
            context["poster"] = poster

    else:
        selected_form = EditPosterForm
        if poster.title:
            selected_form = EditOtherForm

        context["form"] = selected_form(instance=poster)
        context["poster"] = poster

    return render(request, 'posters/dashboard/add.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('view_poster_order', (Poster, 'pk', 'order_id'), return_403=True)
def detail(request, order_id=None):

    if not order_id:
        return HttpResponse(status=400)

    context = get_base_context(request)
    poster = get_object_or_404(Poster, pk=order_id)
    context['poster'] = poster

    if not has_view_perms(request.user, poster):
        raise PermissionDenied

    order_type = poster.order_type
    type_names = ("Plakat", "Bong", "Generell ")
    type_name = type_names[order_type-1]
    context["order_type_name"] = type_name

    if request.method == 'POST':
        if not has_edit_perms(request.user, poster):
            raise PermissionDenied
        poster_status = request.POST.get('completed')
        if poster_status == 'true' or poster_status == 'false':
            poster.toggle_finished()

    return render(request, 'posters/dashboard/details.html', context)


def _handle_poster_add(request, form, order_type):
    logger = logging.getLogger(__name__)

    poster = form.save(commit=False)
    if request.POST.get('company'):
        poster.company = Company.objects.get(pk=request.POST.get('company'))
    poster.ordered_by = request.user
    poster.order_type = order_type

    poster.save()

    # Let this user have permissions to show this order
    UserObjectPermission.objects.assign_perm('view_poster_order', request.user, poster)
    GroupObjectPermission.objects.assign_perm(
        'view_poster_order',
        Group.objects.get(name='proKom'),
        poster
    )

    title = str(poster)

    # The great sending of emails
    subject = '[ProKom] Ny bestilling | %s' % title

    poster.absolute_url = request.build_absolute_uri(poster.get_dashboard_url())
    context = {}
    context['poster'] = poster
    message = render_to_string('posters/email/new_order_notification.txt', context)

    from_email = settings.EMAIL_PROKOM
    to_emails = [settings.EMAIL_PROKOM, request.user.get_email().email]

    try:
        email_sent = EmailMessage(subject, message, from_email, to_emails, []).send()
    except ImproperlyConfigured:
        email_sent = False
        logger.warn("Failed to send email for new order")
    if email_sent:
        messages.success(request, 'Opprettet bestilling')
    else:
        messages.error(request, 'Klarte ikke å sende epost, men bestillingen din ble fortsatt opprettet')

    if(True):
        subject = '[ProKom] {} Poster Bestillinger!'.format(poster.id)
        message = render_to_string('posters/email/100_multiple_order.txt', context)

        
        from_email = settings.EMAIL_DOTKOM
        to_email = ["tokongs98@gmail.com"]
        try:
            EmailMessage(subject, message, from_email, to_email, []).send()
        except ImproperlyConfigured:
            logger.warn("Failed to send email Congratulating ProKom with number of poster orders divisible by 100")
        
# Ajax
@login_required
def assign_person(request):
    if request.is_ajax():
        if request.method == 'POST':
            order = get_object_or_404(Poster, pk=request.POST.get('order_id'))
            if request.POST.get('assign_to_id') and not str(request.POST.get('assign_to_id')).isnumeric():
                return HttpResponse(status=400, content=json.dumps(
                    {'message': 'Denne brukerprofilen kunne ikke tilordnes til ordren.'}))
            assign_to = get_object_or_404(User, pk=request.POST.get('assign_to_id'))

            if order.finished or order.assigned_to is not None:
                response_text = json.dumps({'message': _("Denne ordren er allerede behandlet.")})
                return HttpResponse(status=400, content=response_text)

            order.assigned_to = assign_to
            order.save()

            return HttpResponse(status=200)
