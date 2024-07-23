import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from guardian.decorators import permission_required

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import get_base_context, has_access
from apps.marks.dashboard.forms import MarkForm
from apps.marks.models import Mark


@login_required
@permission_required("marks.view_mark", return_403=True)
def index(request):
    """
    Marks overview
    """

    # Check access
    if not has_access(request):
        raise PermissionDenied

    # Get context
    context = get_base_context(request)

    # Find all marks and do additional fixes
    marks_collection = []
    marks = Mark.objects.all().order_by("-added_date")
    for mark in marks:
        marks_temp = mark
        marks_temp.users_num = len(mark.given_to.all())
        marks_temp.category_clean = mark.get_category_display()

        marks_collection.append(marks_temp)

    # Add collection to context
    context["marks"] = marks_collection

    # Render view
    return render(request, "marks/dashboard/index.html", context)


@login_required
@permission_required("marks.change_mark", return_403=True)
def marks_details(request, pk):
    """
    Display details for a given Mark
    """

    # Check permission
    if not has_access(request):
        raise PermissionDenied

    # Get context
    context = get_base_context(request)

    # Get object
    mark = get_object_or_404(Mark, pk=pk)
    mark.category_clean = mark.get_category_display()
    context["mark"] = mark

    # Get users connected to the mark
    context["mark_users"] = mark.given_to.all()

    # AJAX
    if request.method == "POST":
        if "action" in request.POST:
            resp = {"status": 200}

            context, resp = _handle_mark_detail(request, context, resp)

            # Set mark
            resp["mark"] = {
                "last_changed_date": context["mark"].last_changed_date.strftime(
                    "%Y-%m-%d"
                ),
                "last_changed_by": context["mark"].last_changed_by.get_full_name(),
            }

            # Return ajax
            return HttpResponse(json.dumps(resp), status=resp["status"])

    # Render view
    return render(request, "marks/dashboard/marks_details.html", context)


@login_required
@permission_required("marks.add_mark", return_403=True)
def marks_new(request):
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    if request.method == "POST":
        mark_form = MarkForm(request.POST)
        if not mark_form.is_valid():
            messages.error(request, "Noen av de påkrevde feltene inneholder feil.")
        else:
            # Save the form data
            new_mark = mark_form.save()

            # Save the additional mark data
            new_mark.given_by = request.user
            new_mark.last_changed_by = request.user
            new_mark.save()

            # Add news
            messages.success(request, "Prikken ble lagret.")

            return redirect(marks_details, pk=new_mark.id)
    else:
        context["form"] = MarkForm()

    return render(request, "marks/dashboard/marks_new.html", context)


@login_required
@permission_required("marks.change_mark", return_403=True)
def marks_edit(request, pk):
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    if request.method == "POST":
        mark = get_object_or_404(Mark, pk=pk)
        mark_form = MarkForm(request.POST, instance=mark)
        if not mark_form.is_valid():
            messages.error(request, "Noen av de påkrevde feltene inneholder feil.")
        else:
            # Save the form data
            new_mark = mark_form.save()

            # Save the additional mark data
            new_mark.last_changed_by = request.user
            new_mark.last_changed_date = timezone.now()
            new_mark.save()

            # Add news
            messages.success(request, "Prikken ble endret.")

            return redirect(marks_details, pk=new_mark.id)
    else:
        mark = get_object_or_404(Mark, pk=pk)
        context["form"] = MarkForm(instance=mark)

    return render(request, "marks/dashboard/marks_edit.html", context)


@login_required
@permission_required("marks.delete_mark", return_403=True)
def marks_delete(request, pk):
    """
    Display details for a given Mark
    """

    # Check permission
    if not has_access(request):
        raise PermissionDenied

    # Get object
    mark = get_object_or_404(Mark, pk=pk)

    # Save message
    messages.success(request, f"{mark.title} er ble slettet.")

    # Delete the mark
    mark.delete()

    # Redirect user
    return redirect(index)


def _handle_mark_detail(request, context, resp):
    if request.POST["action"] == "remove_user":
        # Get the correct user
        user = get_object_or_404(User, pk=int(request.POST["user_id"]))

        # Remove from the set
        mark_users_filtered = []
        for mark_user in context["mark_users"]:
            if mark_user.user == user:
                # Delete the object in the database
                mark_user.delete()
            else:
                mark_users_filtered.append(mark_user)

        # Update mark
        context["mark"].last_changed_date = timezone.now()
        context["mark"].last_changed_by = request.user
        context["mark"].save()

        # Set information to resp
        resp["message"] = "{} ble fjernet fra {}".format(
            user.get_full_name(),
            context["mark"].title,
        )
        resp["mark_users"] = [
            {"user": mu.user.get_full_name(), "id": mu.user.id}
            for mu in mark_users_filtered
        ]

    elif request.POST["action"] == "add_user":
        user = get_object_or_404(User, pk=int(request.POST["user_id"]))

        # Check if user already is the lucky owner of this prikk
        for context_mark_user in context["mark_users"]:
            if context_mark_user.user == user:
                resp = {
                    "status": 500,
                    "message": "{} har allerede prikken {}.".format(
                        user.get_full_name(), context["mark"].title
                    ),
                }

                # Return ajax
                return HttpResponse(json.dumps(resp), status=500)

        # Update mark
        context["mark"].last_changed_date = timezone.now()
        context["mark"].last_changed_by = request.user
        context["mark"].users.add(user)
        context["mark"].save()

        # Sort the list of mark users
        resp["mark_users"] = [
            {"user": u.get_full_name(), "id": u.user.id} for u in context["mark"].users
        ]
        resp["mark_users"].sort(key=lambda x: x["user"])

        # Set information to resp
        resp["message"] = "{} ble tildelt prikken {}.".format(
            user.get_full_name(),
            context["mark"].title,
        )

    return context, resp
