# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user
from watson.views import SearchView

from apps.authentication.forms import UserUpdateForm
from apps.authentication.models import AllowedUsername
from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import DashboardPermissionMixin, get_base_context, has_access

from .forms import OnlineGroupForm
from .utils import (
    handle_group_member_add,
    handle_group_member_remove,
    handle_group_role_add,
    handle_group_role_remove,
)


@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, "auth/dashboard/index.html", context)


# GROUP MODULE VIEWS
@login_required
def groups_index(request):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)
    online_groups = get_objects_for_user(
        request.user, "authentication.change_onlinegroup"
    )
    context["groups"] = online_groups

    return render(request, "auth/dashboard/groups_index.html", context)


def groups_detail_post_handler(request, group):
    if request.is_ajax and "action" in request.POST:
        action = request.POST.get("action")
        if action == "remove_user":
            return handle_group_member_remove(request, group)

        elif action == "add_user":
            return handle_group_member_add(request, group)

        elif action == "add_role":
            return handle_group_role_add(request, group)

        elif action == "remove_role":
            return handle_group_role_remove(request, group)

        else:
            return HttpResponse("Ugyldig handling.", status=400)
    else:
        form = OnlineGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Gruppen ble oppdatert")
        else:
            messages.error(request, "Noen av de påkrevde feltene inneholder feil.")
        return redirect(groups_detail, pk=group.id)


@login_required
def groups_detail(request, pk):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)
    online_groups = get_objects_for_user(
        request.user, "authentication.change_onlinegroup"
    )
    group = get_object_or_404(online_groups, pk=pk)
    context["group"] = group
    context["form"] = OnlineGroupForm(instance=group)

    if request.method == "POST":
        return groups_detail_post_handler(request, group)

    if hasattr(settings, "GROUP_SYNCER") and settings.GROUP_SYNCER:
        group_id = int(pk)
        # Groups that list this one as their destination
        context["sync_group_from"] = []
        # Groups that list this one as one of their sources
        context["sync_group_to"] = []

        # Make a dict that simply maps {id: name} for all groups
        groups = {g.id: g.name for g in Group.objects.all().order_by("id")}

        for job in settings.GROUP_SYNCER:
            if group_id in job["source"]:
                context["sync_group_to"].extend(
                    [groups[g_id] for g_id in job["destination"]]
                )
            if group_id in job["destination"]:
                context["sync_group_from"].extend(
                    [groups[g_id] for g_id in job["source"]]
                )

    context["group_users"] = list(group.group.user_set.all())

    context["group_permissions"] = list(group.group.permissions.all())

    context["group_users"].sort(key=lambda x: str(x).lower())
    context["group_permissions"].sort(key=lambda x: str(x))

    return render(request, "auth/dashboard/groups_detail.html", context)


@login_required
@permission_required("authentication.view_allowedusername", return_403=True)
def members_index(request):

    """
    Index overview for allowedusernames in dashboard
    """

    if not has_access(request):
        raise PermissionDenied

    def merge_names(members):
        for i in members:
            user = list(User.objects.filter(ntnu_username=i.username))
            if user:
                i.full_name = user[0].get_full_name()
        return members

    context = get_base_context(request)
    members = AllowedUsername.objects.all()
    context["members"] = merge_names(members)

    return render(request, "auth/dashboard/user_list.html", context)


class UserListView(DashboardPermissionMixin, ListView):
    model = User
    queryset = User.objects.all().exclude(id=-1)
    paginate_by = 25
    paginator_class = Paginator
    permission_required = "authentication.view_onlineuser"
    template_name = "auth/dashboard/user_list.html"


class UserSearchView(DashboardPermissionMixin, SearchView):
    model = User
    queryset = User.objects.all().exclude(id=-1)
    paginate_by = 25
    paginator_class = Paginator
    permission_required = "authentication.view_onlineuser"
    template_name = "auth/dashboard/user_list.html"
    empty_query_redirect = reverse_lazy("user_list")


class UserDetailView(DashboardPermissionMixin, DetailView):
    model = User
    context_object_name = "user"
    permission_required = "authentication.view_onlineuser"
    pk_url_kwarg = "user_id"
    template_name = "auth/dashboard/user_detail.html"


class UserUpdateView(DashboardPermissionMixin, UpdateView):
    form_class = UserUpdateForm
    model = User
    context_object_name = "user"
    permission_required = "authentication.change_onlineuser"
    pk_url_kwarg = "user_id"
    template_name = "auth/dashboard/user_edit.html"

    def get_success_url(self):
        return reverse(
            "dashboard_user_detail", kwargs={"user_id": self.kwargs.get("user_id")}
        )


class UserDeleteView(DashboardPermissionMixin, DeleteView):
    model = User
    permission_required = "authentication.delete_onlineuser"
    pk_url_kwarg = "user_id"
    success_url = reverse_lazy("user_list")


@login_required
@permission_required("authentication.add_allowedusername", return_403=True)
def members_new(request):
    """
    Create new allowedusername form and handling
    """
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, "auth/dashboard/members_new.html", context)
