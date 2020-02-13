# -*- encoding: utf-8 -*-

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user
from watson.views import SearchView

from apps.authentication.constants import RoleType
from apps.authentication.forms import UserUpdateForm
from apps.authentication.models import AllowedUsername, GroupMember, GroupRole
from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import DashboardPermissionMixin, get_base_context, has_access


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
@permission_required("authentication.change_onlineuser", return_403=True)
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


@login_required
@permission_required("authentication.change_onlineuser", return_403=True)
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

    # AJAX
    if request.method == "POST":
        if request.is_ajax and "action" in request.POST:
            resp = {"status": 200}
            if request.POST["action"] == "remove_user":
                user = get_object_or_404(User, pk=int(request.POST["user_id"]))
                member = get_object_or_404(GroupMember, user=user, group=group)
                member.delete()
                user_ids = group.members.values_list("user_id")
                users = User.objects.filter(pk__in=user_ids)
                message = f"{user.get_full_name()} ble fjernet fra {group.name_long}"

                resp["message"] = message
                resp["users"] = [{"user": u.get_full_name(), "id": u.id} for u in users]
                resp["users"].sort(key=lambda x: x["user"])

                return HttpResponse(json.dumps(resp), status=200)

            elif request.POST["action"] == "add_user":
                user = get_object_or_404(User, pk=int(request.POST["user_id"]))
                full_name = user.get_full_name()
                try:
                    member = GroupMember.objects.create(group=group, user=user)
                    member_role = GroupRole.get_for_type(RoleType.MEMBER)
                    member.roles.add(member_role)
                    user_ids = group.members.values_list("user_id")
                    users = User.objects.filter(pk__in=user_ids)

                    resp["full_name"] = full_name
                    resp["users"] = [
                        {"user": u.get_full_name(), "id": u.id} for u in users
                    ]
                    resp["users"].sort(key=lambda x: x["user"])
                    resp["message"] = f"{full_name} ble lagt til i {group.name_long}"

                    return HttpResponse(json.dumps(resp), status=200)
                except IntegrityError:
                    return HttpResponse(
                        f"{full_name} er allerede i gruppen {group.name_long}",
                        status=400,
                    )

        return HttpResponse("Ugyldig handling.", status=400)

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
