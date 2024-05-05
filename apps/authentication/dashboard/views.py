from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView
from guardian.shortcuts import get_objects_for_user

from apps.authentication.models import GroupRole, OnlineGroup
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
    if "action" in request.POST:
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
        form = OnlineGroupForm(data=request.POST, instance=group, user=request.user)
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
    context["form"] = OnlineGroupForm(instance=group, user=request.user)

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

    context["group_permissions"] = list(group.group.permissions.all())
    context["group_permissions"].sort(key=lambda x: str(x))
    context["roles"] = GroupRole.objects.all()

    return render(request, "auth/dashboard/groups_detail.html", context)


class GroupCreateView(DashboardPermissionMixin, CreateView):
    model = OnlineGroup
    form_class = OnlineGroupForm
    template_name = "auth/dashboard/groups_create.html"
    permission_required = "authentication.add_onlinegroup"

    def get_success_url(self):
        return reverse("groups_index")

    def get_form_kwargs(self):
        """Make the requesting user available to the form"""
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        online_group: OnlineGroup = form.save(commit=False)
        django_group = Group.objects.create(name=online_group.name_short)
        online_group.group = django_group
        online_group.save()
        return super().form_valid(form)
