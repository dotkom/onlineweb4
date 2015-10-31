# -*- encoding: utf-8 -*-

import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from guardian.decorators import permission_required
from guardian.models import UserObjectPermission, GroupObjectPermission
from pytz import timezone as tz

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import get_base_context
from apps.posters.forms import AddForm, AddPosterForm, AddBongForm, AddOtherForm, EditPosterForm
from apps.companyprofile.models import Company
from apps.posters.models import Poster
from apps.posters.permissions import has_view_perms, has_view_all_perms, has_edit_perms


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
            poster = form.save(commit=False)
            if request.POST.get('company'):
                poster.company = Company.objects.get(pk=request.POST.get('company'))
            poster.ordered_by = request.user
            poster.order_type = order_type

            poster.save()

            # Let this user have permissions to show this order
            UserObjectPermission.objects.assign_perm('view_poster_order', obj=poster, user=request.user)
            GroupObjectPermission.objects.assign_perm(
                'view_poster_order',
                obj=poster,
                group=Group.objects.get(name='proKom')
            )

            title = unicode(poster)

            # Prettify and localize dates
            event_date = \
                poster.event.event_start.astimezone(tz('Europe/Oslo')).strftime("%-d %B %Y kl %H:%M") \
                if poster.event else poster.display_from
            ordered_date = poster.ordered_date.astimezone(tz('Europe/Oslo')).strftime("%-d %B %Y kl %H:%M")

            # The great sending of emails
            subject = '[ProKom] Ny bestilling for %s' % title
            email_template = """
Det har blitt registrert en ny %(order_type)sbestilling pa Online sine nettsider. Dette er bestilling nummer %(id)s.
\n
Antall og type(r): %(num)s x %(order_type)s%(bongs)s\n
%(poster_order)s (%(event_date)s)\n
Bestilt av %(ordered_by)s i %(ordered_by_committee)s den %(ordered_date)s.\n
\n
For mer informasjon, sjekk ut bestillingen her: %(absolute_url)s
"""
            email_message = '%(message)s%(signature)s' % {
                    'message': _(
                        email_template % {
                            'site': '',
                            'order_type': type_name.lower().rstrip(),
                            'num': '%s' % poster.amount,
                            'bongs': ', %s x bong' % poster.bong if poster.bong > 0 else '' if poster.bong > 0 else '',
                            'ordered_by': poster.ordered_by,
                            'ordered_by_committee': poster.ordered_committee,
                            'id': poster.id,
                            'poster_order': title,
                            'event_date': event_date,
                            'ordered_date': ordered_date,
                            'absolute_url': request.build_absolute_uri(poster.get_dashboard_url())
                        }
                    ),
                    'signature': _('\n\nVennlig hilsen Linjeforeningen Online')
            }
            from_email = settings.EMAIL_PROKOM
            to_emails = [settings.EMAIL_PROKOM, request.user.get_email().email]

            try:
                email_sent = EmailMessage(unicode(subject), unicode(email_message), from_email, to_emails, []).send()
            except ImproperlyConfigured:
                email_sent = False
            if email_sent:
                messages.success(request, 'Opprettet bestilling')
            else:
                messages.error(request, 'Klarte ikke å sende epost, men bestillingen din ble fortsatt opprettet')

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
    context['add_poster_form'] = EditPosterForm()

    if order_id:
        poster = get_object_or_404(Poster, pk=order_id)
    else:
        poster = order_id

    if order_id and request.user != poster.ordered_by and 'proKom' not in request.user.groups.all():
        raise PermissionDenied

    if request.POST:
        form = AddForm(request.POST, instance=poster)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("../detail/"+str(poster.id))

    else:
        context["form"] = AddForm(instance=poster)

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


# Ajax


@login_required
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
