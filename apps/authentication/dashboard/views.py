# -*- encoding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404

from guardian.decorators import permission_required
from reversion import get_for_object as get_history_for_object

from apps.authentication.models import OnlineUser as User
from apps.dashboard.tools import has_access, get_base_context

@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/index.html', context)

# Group module views

@login_required
def groups_index(request):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['groups'] = list(Group.objects.all())
    context['groups'].sort(key=lambda x: str(x).lower())

    return render(request, 'auth/dashboard/groups_index.html', context)

@login_required
def groups_detail(request, pk):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['group'] = get_object_or_404(Group, pk=pk)

    context['group_users'] = list(context['group'].user_set.all())
    context['group_permissions'] = list(context['group'].permissions.all())

    context['group_users'].sort(key=lambda x: str(x).lower())
    context['group_permissions'].sort(key=lambda x: str(x))

    history = get_history_for_object(context['group'])

    field_dicts = []

    for h in history:
        field_dicts.append(repr(h.field_dict))

    context['history'] = field_dicts

    return render(request, 'auth/dashboard/groups_detail.html', context)

@login_required
def members_index(request):
    """
    Index overview for allowedusernames in dashboard
    """
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/members_index.html', context)

@login_required
def members_detail(request, pk):
    """
    Detail view for allowedusername with PK=pk
    """
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/members_detail.html', context)

@login_required
def members_new(request):
    """
    Create new allowedusername form and handling
    """
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/members_new.html', context)


