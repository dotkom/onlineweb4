# -*- encoding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    HttpResponse,
    HttpResponseRedirect,
    get_object_or_404,
    redirect,
    render,
)
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from guardian.decorators import permission_required

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import get_base_context
from apps.posters.forms import (
    AddBongForm,
    AddOtherForm,
    AddPosterForm,
    EditOtherForm,
    EditPosterForm,
)
from apps.posters.models import Poster
from apps.posters.permissions import has_edit_perms, has_view_all_perms, has_view_perms

from .utils import _handle_poster_add, get_poster_admins


@login_required
@permission_required("posters.overview_poster_order", return_403=True)
def index(request):
    context = get_base_context(request)

    # View to show if user not in committee, but wanting to see own orders
    if not has_view_all_perms(request.user):
        context["your_orders"] = [
            x
            for x in Poster.objects.all()
            if request.user.has_perm("view_poster_order", x)
            and request.user in x.ordered_committee.user_set.all()
        ]
        return render(request, "posters/dashboard/index.html", context)

    orders = Poster.objects.all()

    context["new_orders"] = orders.filter(assigned_to=None)
    context["active_orders"] = orders.filter(finished=False).exclude(assigned_to=None)
    context["old_orders"] = orders.filter(finished=True)

    context["workers"] = get_poster_admins()

    return render(request, "posters/dashboard/index.html", context)


@login_required
@permission_required("posters.add_poster_order", return_403=True)
def add(request, order_type=0):
    order_type = int(order_type)
    context = get_base_context(request)
    type_names = ("Plakat", "Bong", "Generell ")
    type_name = type_names[order_type - 1]

    poster = Poster()
    form = None

    if request.method == "POST":
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
            context["form"] = form
            context["form"].fields[
                "ordered_committee"
            ].queryset = request.user.groups.all()
            return render(request, "posters/dashboard/add.html", context)

    context["order_type_name"] = type_name
    context["order_type"] = order_type
    context["can_edit"] = request.user.has_perm("posters.view_poster")

    if order_type == 1:
        AddPosterForm()
    elif order_type == 2:
        AddBongForm()
    elif order_type == 3:
        AddOtherForm()

    forms = (AddPosterForm(), AddBongForm(), AddOtherForm())

    context["form"] = forms[order_type - 1]
    context["form"].fields["ordered_committee"].queryset = request.user.groups.all()

    return render(request, "posters/dashboard/add.html", context)


@ensure_csrf_cookie
@login_required
@permission_required(
    "posters.view_poster_order", (Poster, "pk", "order_id"), return_403=True
)
def edit(request, order_id=None):
    context = get_base_context(request)
    context["add_poster_form"] = AddPosterForm()

    if order_id:
        poster = get_object_or_404(Poster, pk=order_id)
    else:
        poster = order_id

    selected_form = EditPosterForm

    if request.POST:
        if poster.title:
            selected_form = EditOtherForm
        form = selected_form(request.POST, instance=poster)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("../detail/" + str(poster.id))
        else:
            context["form"] = form
            context["poster"] = poster

    else:
        selected_form = EditPosterForm
        if poster.title:
            selected_form = EditOtherForm

        context["form"] = selected_form(instance=poster)
        context["poster"] = poster

    return render(request, "posters/dashboard/add.html", context)


@ensure_csrf_cookie
@login_required
@permission_required(
    "posters.view_poster_order", (Poster, "pk", "order_id"), return_403=True
)
def detail(request, order_id=None):

    if not order_id:
        return HttpResponse(status=400)

    context = get_base_context(request)
    poster = get_object_or_404(Poster, pk=order_id)
    context["poster"] = poster

    if not has_view_perms(request.user, poster):
        raise PermissionDenied

    order_type = poster.order_type
    type_names = ("Plakat", "Bong", "Generell ")
    type_name = type_names[order_type - 1]
    context["order_type_name"] = type_name

    if request.method == "POST":
        if not has_edit_perms(request.user, poster):
            raise PermissionDenied
        poster_status = request.POST.get("completed")
        if poster_status == "true" or poster_status == "false":
            poster.toggle_finished()

    return render(request, "posters/dashboard/details.html", context)


# Ajax
@login_required
def assign_person(request):
    if request.is_ajax():
        if request.method == "POST":
            order = get_object_or_404(Poster, pk=request.POST.get("order_id"))
            if (
                request.POST.get("assign_to_id")
                and not str(request.POST.get("assign_to_id")).isnumeric()
            ):
                return HttpResponse(
                    status=400,
                    content=json.dumps(
                        {
                            "message": "Denne brukerprofilen kunne ikke tilordnes til ordren."
                        }
                    ),
                )
            assign_to = get_object_or_404(User, pk=request.POST.get("assign_to_id"))

            if order.finished or order.assigned_to is not None:
                response_text = json.dumps(
                    {"message": _("Denne ordren er allerede behandlet.")}
                )
                return HttpResponse(status=400, content=response_text)

            order.assigned_to = assign_to
            order.save()

            return HttpResponse(status=200)
